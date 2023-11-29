from typing import OrderedDict, List, Dict, Tuple, Any
import astroid
from zt_backend.models.request import Request,Cell,CodeDict
import duckdb
import uuid
import re
import logging
import traceback

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
    defined_names = [target.name for defnode in module.nodes_of_class(astroid.Assign) for target in defnode.targets if hasattr(target, 'name')]
    func_def_names = [arg.name for func in module.nodes_of_class(astroid.FunctionDef) for arg in func.args.args]
    return list(set(defined_names) - set(func_def_names))

def get_loaded_modules(module) -> List[str]:
    try:
        return [node.expr.name for node in module.nodes_of_class(astroid.Attribute) if hasattr(node.expr, 'name')]
    except Exception as e:
        logger.error("Error getting loaded modules: %s", traceback.format_exc())
        return []

def get_loaded_names(module, defined_names) -> List[str]:
    function_names, function_arguments = get_functions(module)
    return [usenode.name for usenode in module.nodes_of_class(astroid.Name) if usenode.name not in function_arguments]

def generate_sql_code(cell, uuid_value, db_file='my_database.db'):
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
        data_frame_conversion = f"zt.DataFrame.from_dataframe(id='{uuid_value}', df={sql_execution})"
        
        full_code = f"{base_code}\n{db_init}\n{data_frame_conversion}"

    return full_code

def parse_cells(request: Request) -> CodeDict:
    cell_dict = {}
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
            function_names, function_arguments = get_functions(module)
            defined_names = get_defined_names(module) + get_imports(module) + function_names
            loaded_names = get_loaded_names(module, defined_names) + get_loaded_modules(module) + list(table_names)
            cell_dict[cell.id] = Cell(**{
                'code': cell.code,
                'defined_names': defined_names,
                'loaded_names': list(set(loaded_names))})
        except Exception as e:
            logger.error("Error while parsing cells, returning empty names lists: %s", traceback.format_exc())
            cell_dict[cell.id] = Cell(**{
                'code': cell.code,
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

    return graph

def find_child_cells(cell: Cell, code_dictionary: CodeDict, idx: int) -> List[str]:
    child_cells = []
    names = cell.defined_names
    for next_key in list(code_dictionary.cells.keys())[idx + 1:]:
        next_cell = code_dictionary.cells[next_key]
        next_loaded_names = next_cell.loaded_names
        if set(names).intersection(set(next_loaded_names)):
            child_cells.append(next_key)
    return child_cells

def add_parent_cells(code_dictionary: CodeDict) -> Dict[str, Any]:
    for key in list(code_dictionary.cells.keys()):
        cell = code_dictionary.cells[key]
        child_cells = cell.child_cells
        for child_cell in child_cells:
            code_dictionary.cells[child_cell].parent_cells.append(key)
        cell.child_cells = child_cells
    return code_dictionary

def add_child_cells(code_dictionary: CodeDict, prev_components: Dict[str, Any]) -> Dict[str, Any]:
    for idx, key in enumerate(list(code_dictionary.cells.keys())):
        cell = code_dictionary.cells[key]
        cell.child_cells = find_child_cells(cell, code_dictionary, idx)
        cell.previous_child_cells = prev_components.get(key, {}).get('child_cells', [])
    return add_parent_cells(code_dictionary)

def print_astroid_tree(code):
    module = astroid.parse(code)
    print(module.repr_tree())

def find_downstream_cells(code_dictionary: CodeDict, start_cell_id, visited=None):
    if visited is None:
        visited = set()
        
    if start_cell_id in visited:
        return []
    
    visited.add(start_cell_id)
    
    downstream_cells = []
    
    for cell_id, cell_data in code_dictionary.cells.items():
        if start_cell_id in cell_data.parent_cells:
            downstream_cells.append(cell_id)
            downstream_cells.extend(find_downstream_cells(code_dictionary, cell_id, visited))
    
    return list(OrderedDict.fromkeys(downstream_cells))

