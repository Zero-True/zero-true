from io import StringIO
from typing import Dict,Any
import pickle
from contextlib import redirect_stdout
from zt_backend.models import request, response
from zt_backend.models.components.zt_component import ZTComponent
from zt_backend.models.state import component_values, created_components, context_globals, cell_outputs_dict
from zt_backend.runner.code_cell_parser import parse_cells,build_dependency_graph, find_downstream_cells, CodeDict


def try_pickle(obj):
    """
    Attempts to pickle and then unpickle an object. If successful, returns the unpickled object, 
    otherwise returns the original object.
    """
    try:
        return pickle.loads(pickle.dumps(obj))
    except Exception as e:
        return obj


def get_parent_vars(cell_id: str, code_components: CodeDict, cell_outputs_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Gathers and returns parent variables for a given cell.

    Args:
        cell (str): ID of the current cell.
        code_components (dict): Mapping of all cell IDs to their related components such as parent cells, code, etc.
        cell_outputs_dict (dict): Contains outputs of all previously executed cells.

    Returns:
        dict: Dictionary containing the parent variables for the cell.
    """  
    #print(code_components)
    if cell_id not in code_components.cells:
        # Print localstorage_data and stop execution if cell is not in code_components
        for key in cell_outputs_dict.keys():
            print('Key',key, 'Value', cell_outputs_dict[key])
        raise KeyError(f"'{cell_id}' is not present in code_components. Execution stopped.")

    parent_vars = []
    parent_cells = code_components.cells[cell_id].parent_cells
    cell_dicts = []
    for parent_cell in parent_cells:
        cell_dicts.append(cell_outputs_dict.get(parent_cell, {}))
        parent_vars_list = code_components.cells[parent_cell].loaded_names + \
                           code_components.cells[parent_cell].defined_names
        parent_vars += parent_vars_list

    exec_parents = {key: try_pickle(val) for d in cell_dicts for key, val in d.items() if key in code_components.cells[cell_id].loaded_names}

    return exec_parents


#issue right now is that the request is sending the entire notebook. The request should send the ID of the cell you are running.
#also right now there is no special handling for the 
def execute_request(request: request.Request):
    context_globals['exec_mode'] = True
    cell_outputs = []
    component_values.update(request.components)
    component_globals={'global_state': component_values}
    added_components = []
    dependency_graph = build_dependency_graph(parse_cells(request))
    downstream_cells = [request.originId]
    downstream_cells.extend(find_downstream_cells(dependency_graph, request.originId))
 

    #go through each item in dependency graph (we should just go through the downstream cells)
    for code_cell_id in downstream_cells:
        code_cell = dependency_graph.cells[code_cell_id]

        f = StringIO()
        with redirect_stdout(f):
            try:
                if code_cell.parent_cells == []:
                    temp_globals = component_globals
                else:
                    temp_globals = get_parent_vars(cell_id=code_cell_id,code_components=dependency_graph,cell_outputs_dict=cell_outputs_dict)

                for component_name, value in temp_globals.items():
                    if isinstance(value, ZTComponent) and value.id not in added_components:
                        value.variable_name = component_name
                        added_components.append(value.id)
                exec(code_cell.code, temp_globals)
            except Exception as e:
                print(e)
        response_components = []
        cell_outputs_dict[code_cell_id] = {k: try_pickle(v) for k, v in temp_globals.items() if k != '__builtins__'}

        for component_name, value in temp_globals.items():
            if isinstance(value, ZTComponent) and value.id not in added_components:
                value.variable_name = component_name
                added_components.append(value.id)
                response_components.append(value)
        cell_outputs.append(response.CellResponse(id=code_cell_id, components=response_components, output=f.getvalue()))


    component_values.clear()
    created_components.clear()
    context_globals['exec_mode'] = False
    return response.Response(cells=cell_outputs)