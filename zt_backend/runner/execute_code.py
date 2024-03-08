from typing import Dict, Any, OrderedDict
from io import StringIO
import pickle
from zt_backend.models.api import request, response
from zt_backend.runner.code_cell_parser import parse_cells, build_dependency_graph, CodeDict
from zt_backend.models.state.user_state import UserState, UserContext
from zt_backend.models.state.state import State
from zt_backend.models.components.layout import Layout
from zt_backend.utils.notebook import globalStateUpdate
from zt_backend.config import settings
from datetime import datetime
import logging
import traceback
import contextlib

now = datetime.now()
logger = logging.getLogger("__name__")

def try_pickle(obj):
    """
    Attempts to pickle and then unpickle an object. If successful, returns the unpickled object, 
    otherwise returns the original object.
    """
    if isinstance(obj, State):
        return obj
    try:
        return pickle.loads(pickle.dumps(obj))
    except Exception as e:
        logger.debug("Error during pickle: %s", e)
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
    if cell_id not in code_components.cells:
        # Print localstorage_data and stop execution if cell is not in code_components
        for key in cell_outputs_dict.keys():
            logger.debug("Key: %s, Value: %s", key, cell_outputs_dict[key])
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

def execute_request(request: request.Request, state: UserState):
    with UserContext(state) as execution_state:
        logger.debug("Code execution started")
        cell_outputs = []
        execution_state.component_values.update(request.components)
        component_globals={'global_state': execution_state.component_values}
        dependency_graph = build_dependency_graph(parse_cells(request))
        if request.originId:
            downstream_cells = [request.originId]+dependency_graph.cells[request.originId].child_cells
            try:
                old_downstream_cells = [request.originId]
                # Find cells that are no longer dependent
                no_longer_dependent_cells = set(old_downstream_cells) - set(downstream_cells)
        
                if no_longer_dependent_cells:
                    downstream_cells.extend(list(OrderedDict.fromkeys(no_longer_dependent_cells)))
            except Exception as e:
                logger.error("Error while updating cell dependencies: %s", traceback.format_exc())
        else:
            downstream_cells = [cell.id for cell in request.cells if cell.cellType in ['code', 'sql']]
        for code_cell_id in downstream_cells:
            code_cell = dependency_graph.cells[code_cell_id]
            if code_cell_id!=request.originId and code_cell.nonReactive:
                continue
            execution_state.message_queue.put_nowait({"cell_id": code_cell_id, "clear_output": True})
            execution_state.io_output = StringIO()
            execute_cell(code_cell_id, code_cell, component_globals, dependency_graph, execution_state)
            try:
                layout = execution_state.current_cell_layout[0]
            except Exception as e:
                logger.debug("Error while getting cell layout, setting empty layout: %s", traceback.format_exc())
                layout = Layout(**{})
            for component in execution_state.current_cell_components:
                if component.component == 'v-btn' or component.component == 'v-timer':
                    component.value = False

            cell_response = response.CellResponse(id=code_cell_id, layout=layout, components=execution_state.current_cell_components, output=execution_state.io_output.getvalue())
            cell_outputs.append(cell_response)
            execution_state.message_queue.put_nowait(cell_response.model_dump_json())
            execution_state.current_cell_components.clear()
            execution_state.current_cell_layout.clear()
        execution_state.cell_outputs_dict['previous_dependecy_graph'] = dependency_graph
        execution_state.component_values.clear()
        execution_state.created_components.clear()
        execution_state.context_globals['exec_mode'] = False
        execution_response = response.Response(cells=cell_outputs)
        execution_state.message_queue.put_nowait({"complete": True})
        if settings.run_mode=='dev':
            globalStateUpdate(run_response=execution_response,run_request=request)


def execute_cell(code_cell_id, code_cell, component_globals, dependency_graph, execution_state: UserContext):
    class WebSocketStream:
        def write(self, message):
            user_state = UserContext.get_state()
            if user_state:
                user_state.io_output.write(message)
                user_state.message_queue.put_nowait({"cell_id": code_cell_id, "output": message})

        def flush(self):
            pass
    with contextlib.redirect_stdout(WebSocketStream()), \
        contextlib.redirect_stderr(WebSocketStream()):
        try:
            if code_cell.parent_cells == []:
                temp_globals = component_globals
            else:
                temp_globals = get_parent_vars(cell_id=code_cell_id,code_components=dependency_graph,cell_outputs_dict=execution_state.cell_outputs_dict)
            execution_state.context_globals['exec_mode'] = True
            exec(code_cell.code, temp_globals)

        except Exception:
            logger.debug("Error during code execution")
            tb_list = traceback.format_exc().splitlines(keepends=True)
            tb_list = [tb_list[0]]+tb_list[3:]
            print("".join(tb_list))
    execution_state.context_globals['exec_mode'] = False
    #exclude builtins and State objectcts
    execution_state.cell_outputs_dict[code_cell_id] = {k: try_pickle(v) for k, v in temp_globals.items() if k != '__builtins__'}