from fastapi import WebSocket
from typing import Dict,Any,OrderedDict
import pickle
from zt_backend.models import request, response
from zt_backend.models.state import component_values, created_components, context_globals, current_cell_components,current_cell_layout
from zt_backend.runner.code_cell_parser import parse_cells,build_dependency_graph, find_downstream_cells, CodeDict
from zt_backend.models.components.layout import Layout
from datetime import datetime
import logging
import traceback
import contextlib
import asyncio
import threading
import sys
import trace
import time

now = datetime.now()
logger = logging.getLogger("__name__")

class KThread(threading.Thread):
  """A subclass of threading.Thread, with a kill()
method."""
  def __init__(self, *args, **keywords):
    threading.Thread.__init__(self, *args, **keywords)
    self.killed = False

  def start(self):
    """Start the thread."""
    self.__run_backup = self.run
    self.run = self.__run      # Force the Thread to install our trace.
    threading.Thread.start(self)

  def __run(self):
    """Hacked run function, which installs the
trace."""
    sys.settrace(self.globaltrace)
    self.__run_backup()
    self.run = self.__run_backup

  def globaltrace(self, frame, why, arg):
    if why == 'call':
      return self.localtrace
    else:
      return None

  def localtrace(self, frame, why, arg):
    if self.killed:
      if why == 'line':
        raise SystemExit()
    return self.localtrace

  def kill(self):
    self.killed = True

def try_pickle(obj):
    """
    Attempts to pickle and then unpickle an object. If successful, returns the unpickled object, 
    otherwise returns the original object.
    """
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


#issue right now is that the request is sending the entire notebook. The request should send the ID of the cell you are running.
async def execute_request(request: request.Request, cell_outputs_dict: Dict, websocket: WebSocket):
    logger.debug("Code execution started")
    cell_outputs = []
    component_values.update(request.components)
    component_globals={'global_state': component_values}
    dependency_graph = build_dependency_graph(parse_cells(request))
    if request.originId:
        downstream_cells = [request.originId]
        downstream_cells.extend(find_downstream_cells(dependency_graph, request.originId))

        try:
            old_downstream_cells = [request.originId]
            old_downstream_cells.extend(find_downstream_cells(cell_outputs_dict['previous_dependecy_graph'],request.originId))
             # Find cells that are no longer dependent
            no_longer_dependent_cells = set(old_downstream_cells) - set(downstream_cells)
    
            if no_longer_dependent_cells:
                downstream_cells.extend(list(OrderedDict.fromkeys(no_longer_dependent_cells)))
        except Exception as e:
            logger.error("Error while updating cell dependencies: %s", traceback.format_exc())
    else:
        downstream_cells = [cell.id for cell in request.cells if cell.cellType in ['code', 'sql']]
 
    global current_thread
    code_cell_id = ""
    current_thread = None
    while(downstream_cells):
        if current_thread and current_thread.is_alive():
           time.sleep(0.1)
           continue
        if code_cell_id:
            try:
                layout = current_cell_layout[0]
            except Exception as e:
                logger.debug("Error while getting cell layout, setting empty layout: %s", traceback.format_exc())
                layout = Layout(**{})
            
            for component in current_cell_components:
                if component.component == 'v-btn':
                    component.value = False
            cell_response = response.CellResponse(id=code_cell_id,layout=layout, components=current_cell_components, output="")
            cell_outputs.append(cell_response)
            await websocket.send_json(cell_response.model_dump_json())
            downstream_cells.pop(0)
        current_cell_components.clear()
        current_cell_layout.clear()
        if downstream_cells:
            code_cell_id = downstream_cells[0]
            code_cell = dependency_graph.cells[code_cell_id]
            await websocket.send_json({"cell_id": code_cell_id, "clear_output": True})
            current_thread = KThread(target=execute_cell, args=(code_cell_id, code_cell, component_globals, dependency_graph, cell_outputs_dict, websocket))
            current_thread.start()
    cell_outputs_dict['previous_dependecy_graph'] = dependency_graph
    component_values.clear()
    created_components.clear()
    context_globals['exec_mode'] = False
    return response.Response(cells=cell_outputs)


    #go through each item in dependency graph (we should just go through the downstream cells)
    # for code_cell_id in list(OrderedDict.fromkeys(downstream_cells)):
    #     # code_cell = dependency_graph.cells[code_cell_id]
    #     f = StringIO()
    #     with redirect_stdout(f):
    #         try:
    #             if code_cell.parent_cells == []:
    #                 temp_globals = component_globals
    #             else:
    #                 temp_globals = get_parent_vars(cell_id=code_cell_id,code_components=dependency_graph,cell_outputs_dict=cell_outputs_dict)
    #             context_globals['exec_mode'] = True
    #             exec(code_cell.code, temp_globals)

    #         except Exception as e:
    #             logger.debug("Error during code execution")
    #             tb_list = traceback.format_exc().splitlines(keepends=True)
    #             tb_list = [tb_list[0]]+tb_list[3:]
    #             print("".join(tb_list))
                

    #     context_globals['exec_mode'] = False
    #     cell_outputs_dict[code_cell_id] = {k: try_pickle(v) for k, v in temp_globals.items() if k != '__builtins__'}

        # try:
        #     layout = current_cell_layout[0]
        # except Exception as e:
        #     logger.debug("Error while getting cell layout, setting empty layout: %s", traceback.format_exc())
        #     layout = Layout(**{})
        
        # for component in current_cell_components:
        #     if component.component == 'v-btn':
        #         component.value = False

        # cell_outputs.append(response.CellResponse(id=code_cell_id,layout=layout, components=current_cell_components, output=f.getvalue()))
        # current_cell_components.clear()
        # current_cell_layout.clear()
    
    # cell_outputs_dict['previous_dependecy_graph'] = dependency_graph

    # component_values.clear()
    # created_components.clear()
    # context_globals['exec_mode'] = False
    # return response.Response(cells=cell_outputs)

def execute_cell(code_cell_id, code_cell, component_globals, dependency_graph, cell_outputs_dict, websocket):
    class WebSocketStream:
        def __init__(self, websocket):
            self.websocket = websocket

        def write(self, message):
            asyncio.run(self.websocket.send_json({"cell_id": code_cell_id, "output": message}))

        def flush(self):
            pass
    with contextlib.redirect_stdout(WebSocketStream(websocket)), \
         contextlib.redirect_stderr(WebSocketStream(websocket)):
        try:
            if code_cell.parent_cells == []:
                temp_globals = component_globals
            else:
                temp_globals = get_parent_vars(cell_id=code_cell_id,code_components=dependency_graph,cell_outputs_dict=cell_outputs_dict)
            context_globals['exec_mode'] = True
            exec(code_cell.code, temp_globals)

        except Exception:
            logger.debug("Error during code execution")
            tb_list = traceback.format_exc().splitlines(keepends=True)
            tb_list = [tb_list[0]]+tb_list[3:]
            print("".join(tb_list))
            
    context_globals['exec_mode'] = False
    cell_outputs_dict[code_cell_id] = {k: try_pickle(v) for k, v in temp_globals.items() if k != '__builtins__'}