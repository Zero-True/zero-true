from typing import List, Dict, Tuple, Any
import astroid
from zt_backend.models.api.request import Request, Cell, CodeDict
import duckdb
import uuid
import re
import logging
import traceback
from zt_backend.config import settings
from datetime import datetime, date


logger = logging.getLogger("__name__")


def get_imports(module) -> List[str]:
    import_froms = [
        node.names[0][1] or node.names[0][0]
        for node in module.nodes_of_class(astroid.ImportFrom)
    ]
    imports = [
        node.names[0][1] or node.names[0][0]
        for node in module.nodes_of_class(astroid.Import)
    ]
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
            if hasattr(target, "name"):  # Directly has a name (e.g., AssignName)
                defined_names.append(target.name)
            elif isinstance(target, astroid.Subscript):  # Is a subscript
                if hasattr(target.value, "name"):
                    defined_names.append(target.value.name)
    func_def_names = [
        arg.name
        for func in module.nodes_of_class(astroid.FunctionDef)
        for arg in func.args.args
    ]
    return list((set(defined_names) & set(func_def_names)) | (set(defined_names) - set(func_def_names)))


def get_loaded_modules(module, all_imports) -> List[str]:
    try:
        return list(
            set(
                [
                    node.expr.name
                    for node in module.nodes_of_class(astroid.Attribute)
                    if hasattr(node.expr, "name") and node.expr.name in all_imports
                ]
            )
        )
    except Exception as e:
        logger.error("Error getting loaded modules: %s", traceback.format_exc())
        return []


def get_loaded_names(module, defined_names) -> List[str]:
    function_names, function_arguments = get_functions(module)
    aug_names = [
        node.target.name
        for node in module.nodes_of_class(astroid.AugAssign)
        if isinstance(node.target, astroid.AssignName)
    ]
    return [
        usenode.name
        for usenode in module.nodes_of_class(astroid.Name)
        if usenode.name not in function_arguments
    ] + aug_names


def format_value_for_sql(value: Any) -> str:
    """
    Formats a Python value into its SQL-compatible string representation.
    """
    if value is None:
        return 'NULL'
    elif isinstance(value, bool):
        return str(value).lower()
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, (list, tuple, set)):
        if not value:
            return '(NULL)'
        elements = [format_value_for_sql(v) for v in value]
        return f"({', '.join(elements)})"
    elif isinstance(value, (date, datetime)):
        return f"'{value.isoformat()}'"
    elif isinstance(value, str):
        return f"'{value}'"
    else:
        return f"'{str(value)}'"

def extract_value_from_node(node: astroid.NodeNG) -> Any:
    """
    Extracts value from an AST node.
    """
    if isinstance(node, astroid.Const):
        return node.value
    elif isinstance(node, (astroid.List, astroid.Set)):
        return [extract_value_from_node(elt) for elt in node.elts]
    elif isinstance(node, astroid.Tuple):
        return tuple(extract_value_from_node(elt) for elt in node.elts)
    elif isinstance(node, astroid.Dict):
        if node.items:
            return {
                extract_value_from_node(key): extract_value_from_node(value)
                for key, value in node.items
            }
        return {}
    elif isinstance(node, astroid.Call):
        if isinstance(node.func, astroid.Name):
            if node.func.name == 'date' and len(node.args) == 3:
                try:
                    year, month, day = [extract_value_from_node(arg) for arg in node.args]
                    return date(year, month, day)
                except:
                    logger.warning(f"Failed to create date from args: {node.args}")
            elif node.func.name == 'datetime' and len(node.args) >= 3:
                try:
                    args = [extract_value_from_node(arg) for arg in node.args]
                    return datetime(*args)
                except:
                    logger.warning(f"Failed to create datetime from args: {node.args}")
    return None

def extract_variables(code: str) -> Dict[str, Any]:
    """
    Extracts variable assignments from Python code.
    """
    try:
        module = astroid.parse(code)
        variables = {}
        
        for node in module.body:
            if isinstance(node, astroid.Assign):
                value = extract_value_from_node(node.value)
                if value is not None:
                    for target in node.targets:
                        if isinstance(target, astroid.AssignName):
                            variables[target.name] = value
            
        return variables
    except Exception as e:
        logger.error(f"Error extracting variables: {str(e)}")
        return {}

def resolve_sql_variables(sql_code: str, cells: List['Cell'], current_cell_id: str) -> Tuple[str, List[str]]:
    """
    Resolves variables in SQL and returns modified SQL with resolved values.
    """
    variables = {}
    for cell in cells:
        if cell.id == current_cell_id:
            break
        if cell.cellType == "code":
            cell_vars = extract_variables(cell.code)
            variables.update(cell_vars)
    
    logger.debug(f"Found variables: {variables}")
    resolved_sql = sql_code
    
    # Handle variable substitutions
    for var_name, value in variables.items():
        placeholder = f"{{{var_name}}}"
        if placeholder in resolved_sql:
            resolved_sql = resolved_sql.replace(placeholder, format_value_for_sql(value))
    
    logger.debug(f"Resolved SQL: {resolved_sql}")
    
    # Extract table names
    table_pattern = r"(?i)(?:FROM|JOIN|INTO|UPDATE|TABLE)\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?)"
    table_names = re.findall(table_pattern, resolved_sql)
    unique_tables = list(dict.fromkeys(table_names))
    
    return resolved_sql, unique_tables

def generate_sql_code(cell, uuid_value: str, db_file: str = "zt_db.db") -> str:
    """
    Generates executable SQL code with proper connection handling and DataFrame conversion.
    SQL code is assumed to have all variables already resolved.
    """
    conn_id = str(uuid.uuid4())[:8]
    code_parts = [
        "import duckdb\nimport zero_true as zt",
        f"conn_{conn_id} = duckdb.connect('{db_file}')",
        "query_result = None",  # Initialize query_result
    ]
    
    # Log the SQL being executed for debugging
    code_parts.extend([
        "try:",
        f'    query_result = conn_{conn_id}.execute("""{cell.code}""").df()',
        "except duckdb.CatalogException as e:",
        "    if 'does not exist' in str(e) and ('CREATE' in cell.code.upper() or 'INSERT' in cell.code.upper()):",
        "        # For CREATE/INSERT queries, we don't need to fetch results",
        f'        conn_{conn_id}.execute("""{cell.code}""")',
        "    else:",
        "        raise",
        "except Exception as e:",
        "    print(f'Error executing SQL: {str(e)}')",  # Add error logging
        "    raise"
    ])
    
    # Only handle the result if we got one
    code_parts.append("if query_result is not None:")
    if cell.variable_name:
        code_parts.extend([
            f"    {cell.variable_name} = query_result",
            f"    zt.DataFrame.from_dataframe(id='{uuid_value}', df={cell.variable_name})"
        ])
    else:
        conversion = ("    query_result" if settings.run_mode == "app" and not cell.showTable 
                     else f"    zt.DataFrame.from_dataframe(id='{uuid_value}', df=query_result)")
        code_parts.append(conversion)
    
    code_parts.append(f"conn_{conn_id}.close()")
    return "\n".join(code_parts)

def parse_cells(request: Request) -> CodeDict:
    cell_dict = {}
    all_imports = []
    parse_exceptions = {}
    for cell in [c for c in request.cells if c.cellType in ["code", "sql"]]:
        table_names = []
        if cell.cellType == "sql" and cell.code:
            try:
                # Get SQL with resolved table names and list of tables
                resolved_sql, table_names = resolve_sql_variables(cell.code, request.cells, cell.id)
                # Update cell code with resolved table names
                cell.code = resolved_sql
            except Exception as e:
                logger.error("Error getting table names: %s", traceback.format_exc())
            uuid_value = str(uuid.uuid4())
            cell.code = generate_sql_code(cell, uuid_value)

        try:
            module = astroid.parse(cell.code)
            all_imports += get_imports(module)
            function_names, function_arguments = get_functions(module)
            defined_names = get_defined_names(module) + function_names
            loaded_names = [
                name
                for name in get_loaded_names(module, defined_names)
                + get_loaded_modules(module, all_imports)
                + list(table_names)
                if name not in get_imports(module)
            ]
            cell_dict[cell.id] = Cell(
                **{
                    "code": cell.code,
                    "nonReactive": cell.nonReactive,
                    "defined_names": defined_names,
                    "imported_modules": get_imports(module),
                    "loaded_modules": get_loaded_modules(module, all_imports),
                    "loaded_names": list(set(loaded_names)),
                }
            )
        except Exception as e:
            parse_exceptions[cell.id] = str(e)
            cell_dict[cell.id] = Cell(
                **{
                    "code": cell.code,
                    "nonReactive": cell.nonReactive,
                    "defined_names": [],
                    "loaded_names": [],
                }
            )

    return CodeDict(cells=cell_dict, exceptions=parse_exceptions)


def build_dependency_graph(
    cell_dict: Dict[int, Dict[str, Any]]
) -> Dict[int, Dict[str, Any]]:
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


def find_child_cells(
    cell: Cell, code_dictionary: CodeDict, idx: int, visited_cells=None
) -> List[str]:
    child_cells = []
    names = cell.defined_names
    child_defined_names = []
    for next_key in list(code_dictionary.cells.keys())[idx + 1 :]:
        next_cell = code_dictionary.cells[next_key]
        next_loaded_names = next_cell.loaded_names
        next_loaded_modules = next_cell.loaded_modules
        next_defined_names = next_cell.defined_names
        if set(names + child_defined_names).intersection(
            set(next_loaded_names) - set(next_loaded_modules)
        ):
            child_cells.append(next_key)
            child_defined_names += next_defined_names

    return child_cells


def add_parent_cells(code_dictionary: CodeDict) -> CodeDict:
    for key in list(code_dictionary.cells.keys()):
        cell = code_dictionary.cells[key]
        cell.parent_cells = find_parent_cells(cell, key, code_dictionary)
    return code_dictionary


def find_parent_cells(cell: Cell, key, code_dictionary: CodeDict) -> List[str]:
    parent_cells = []
    names = cell.loaded_names + cell.loaded_modules
    for prev_key in list(code_dictionary.cells.keys()):
        if prev_key == key:
            break
        prev_cell = code_dictionary.cells[prev_key]
        prev_defined_names = (
            prev_cell.defined_names
            + prev_cell.loaded_names
            + prev_cell.loaded_modules
            + prev_cell.imported_modules
        )
        if set(names).intersection(set(prev_defined_names)):
            parent_cells.append(prev_key)
    return parent_cells


def add_child_cells(
    code_dictionary: CodeDict, prev_components: Dict[str, Any]
) -> Dict[str, Any]:
    for idx, key in enumerate(list(code_dictionary.cells.keys())):
        cell = code_dictionary.cells[key]
        cell.child_cells = find_child_cells(cell, code_dictionary, idx)
        cell.previous_child_cells = prev_components.get(key, {}).get("child_cells", [])
    return add_parent_cells(code_dictionary)


def print_astroid_tree(code):
    module = astroid.parse(code)
    print(module.repr_tree())
