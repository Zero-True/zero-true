from typing import List, Dict, Tuple, Any
import astroid
from zt_backend.models.api.request import Request,Cell,CodeDict
import duckdb
import uuid
import re
import logging
import traceback
from zt_backend.config import settings


logger = logging.getLogger("__name__")

def get_imports(module) -> List[str]:
    import_froms = [node.names[0][1] or node.names[0][0] for node in module.nodes_of_class(astroid.ImportFrom)]
    imports = [node.names[0][1] or node.names[0][0] for node in module.nodes_of_class(astroid.Import)]
    return import_froms + imports

def get_functions(module) -> Tuple[List[str], List[str]]:
    function_names = []
    argument_names = []
    for function_def in module.nodes_of_class(astroid.FunctionDef):
        function_names.append(function_def.name)
        argument_names.extend([arg.name for arg in function_def.args.args])
    return function_names, argument_names

def get_defined_names(module) -> List[str]:
    defined_names = []
    for defnode in module.nodes_of_class(astroid.Assign):
        for target in defnode.targets:
            if hasattr(target, 'name'):  # Directly has a name (e.g., AssignName)
                defined_names.append(target.name)
            elif isinstance(target, astroid.Subscript):  # Is a subscript
                if hasattr(target.value, 'name'):
                    defined_names.append(target.value.name)    
    func_def_names = [arg.name for func in module.nodes_of_class(astroid.FunctionDef) for arg in func.args.args]
    return list(set(defined_names) - set(func_def_names))

def get_loaded_modules(module,all_imports) -> List[str]:
    try:
        return list(set([node.expr.name for node in module.nodes_of_class(astroid.Attribute) if hasattr(node.expr, 'name') and node.expr.name in all_imports]))
    except Exception as e:
        logger.error("Error getting loaded modules: %s", traceback.format_exc())
        return []

def get_loaded_names(module, defined_names) -> List[str]:
    function_names, function_arguments = get_functions(module)
    aug_names = [node.target.name for node in module.nodes_of_class(astroid.AugAssign) if isinstance(node.target, astroid.AssignName)]
    return [usenode.name for usenode in module.nodes_of_class(astroid.Name) if usenode.name not in function_arguments]+aug_names

def generate_sql_code(cell, uuid_value, db_file='zt_db.db'):
    """Generate SQL code for the given cell."""
    
    # Common import statements
    base_code = "import duckdb\nimport zero_true as zt"

    # Initialize the DuckDB database connection to persist tables
    db_init = f"conn = duckdb.connect('{db_file}')"

    # Extract all placeholders from the SQL string
    placeholders = re.findall(r"\{(.*?)\}", cell.code)
    
    # Replace placeholders with "?" for SQL parameterization
    parametrized_sql = re.sub(r"\{(.*?)\}", "?", cell.code)
    
    # SQL code execution
    sql_execution = f'conn.execute("""{parametrized_sql}""", [{", ".join(placeholders)}]).df()'

    if cell.variable_name:
        # If variable_name is provided, use it for assignment
        variable_assignment = f"{cell.variable_name} = {sql_execution}"

        # Convert the result to a custom DataFrame
        data_frame_conversion = f"zt.DataFrame.from_dataframe(id='{uuid_value}', df={cell.variable_name})"
        
        full_code = f"{base_code}\n{db_init}\n{variable_assignment}\n{data_frame_conversion}"
        
    else:
        # If variable_name is not provided, directly use the SQL execution
        if settings.run_mode == 'app' and not cell.showTable:
            data_frame_conversion = ''
        else:
            data_frame_conversion = f"zt.DataFrame.from_dataframe(id='{uuid_value}', df={sql_execution})"
        
        full_code = f"{base_code}\n{db_init}\n{data_frame_conversion}"

    return full_code

def parse_cells(request: Request) -> CodeDict:
    cell_dict = {}
    all_imports = []
    for cell in [c for c in request.cells if c.cellType in ['code', 'sql']]:
        table_names=[]
        if cell.cellType=='sql' and cell.code:
            try:
                table_names = duckdb.get_table_names(re.sub(r'\{.*?\}', '1', cell.code))
            except Exception as e:
                print(e)
            uuid_value = str(uuid.uuid4())
            cell.code = generate_sql_code(cell, uuid_value)
        
        try:
            module = astroid.parse(cell.code)
            all_imports += get_imports(module)
            function_names, function_arguments = get_functions(module)
            defined_names = get_defined_names(module) + function_names
            loaded_names = [name for name in get_loaded_names(module, defined_names) + get_loaded_modules(module,all_imports) + list(table_names) if name not in get_imports(module)]
            cell_dict[cell.id] = Cell(**{
                'code': cell.code,
                'nonReactive': cell.nonReactive,
                'defined_names': defined_names,
                'imported_modules':get_imports(module),
                'loaded_modules':get_loaded_modules(module,all_imports),
                'loaded_names': list(set(loaded_names))})
        except Exception as e:
            logger.error("Error while parsing cells, returning empty names lists: %s", traceback.format_exc())
            cell_dict[cell.id] = Cell(**{
                'code': cell.code,
                'nonReactive': cell.nonReactive,
                'defined_names': [],
                'loaded_names': []})
    
    return CodeDict(cells=cell_dict)


def build_dependency_graph(cell_dict: Dict[int, Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    """
    Builds a dependency graph from a cell dictionary. Each node in the graph represents a cell,
    and edges represent dependencies between cells based on loaded and defined names.
    """
    # Initialize previous components dictionary
    prev_components = {}

    # Add child and parent relationships
    graph = add_child_cells(cell_dict, prev_components)
    # Add previous child cells
    return graph

def find_child_cells(cell: Cell, code_dictionary: CodeDict, idx: int, visited_cells=None) -> List[str]:
    child_cells = []
    names = cell.defined_names
    child_defined_names = []
    for next_key in list(code_dictionary.cells.keys())[idx + 1:]:
        next_cell = code_dictionary.cells[next_key]
        next_loaded_names = next_cell.loaded_names
        next_loaded_modules = next_cell.loaded_modules
        next_defined_names = next_cell.defined_names
        if set(names+child_defined_names).intersection(set(next_loaded_names)-set(next_loaded_modules)):
            child_cells.append(next_key)
            child_defined_names += next_defined_names

    return child_cells
    

def add_parent_cells(code_dictionary: CodeDict) -> CodeDict:
    for key in list(code_dictionary.cells.keys()):
        cell = code_dictionary.cells[key]
        cell.parent_cells = find_parent_cells(cell,key, code_dictionary)
    return code_dictionary

def find_parent_cells(cell: Cell,key, code_dictionary: CodeDict) -> List[str]:
    parent_cells = []
    names = cell.loaded_names+cell.loaded_modules
    for prev_key in list(code_dictionary.cells.keys()):
        if prev_key == key:
            break
        prev_cell = code_dictionary.cells[prev_key]
        prev_defined_names = prev_cell.defined_names+prev_cell.loaded_names+prev_cell.loaded_modules+prev_cell.imported_modules
        if set(names).intersection(set(prev_defined_names)):
            parent_cells.append(prev_key)
    return parent_cells



def add_child_cells(code_dictionary: CodeDict, prev_components: Dict[str, Any]) -> Dict[str, Any]:
    for idx, key in enumerate(list(code_dictionary.cells.keys())):
        cell = code_dictionary.cells[key]
        cell.child_cells = find_child_cells(cell, code_dictionary, idx)
        cell.previous_child_cells = prev_components.get(key, {}).get('child_cells', [])
    return add_parent_cells(code_dictionary)

def print_astroid_tree(code):
    module = astroid.parse(code)
    print(module.repr_tree())

