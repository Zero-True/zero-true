import subprocess
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from zt_backend.models import request, notebook
from zt_backend.runner.execute_code import execute_request
from zt_backend.config import settings
from zt_backend.utils import *
from zt_backend.runner.user_state import UserState
from fastapi.responses import HTMLResponse
from copilot.copilot import text_document_did_change
import logging
import site
import uuid
import os
import threading
import traceback
import sys
import asyncio
import pkg_resources
import trace

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_text(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

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

router = APIRouter()
manager = ConnectionManager()
current_path = os.path.dirname(os.path.abspath(__file__))

#connect to db for saving notebook
notebook_db_dir =  site.USER_SITE+'/.zero_true/'
notebook_db_path = notebook_db_dir+'notebook.db'
os.makedirs(notebook_db_dir, exist_ok=True)

user_states={}
user_timers={}
user_threads={}
user_message_tasks={}
notebook_state=UserState('')
run_mode = settings.run_mode
save_queue = asyncio.Queue()

logger = logging.getLogger("__name__")

@router.get("/app", response_class=HTMLResponse)
async def catch_all():
    if(run_mode=='dev'):
        return HTMLResponse(open(os.path.join(current_path, "dist_dev", "index.html")).read())

@router.get("/health")
def health():
    return('UP')

@router.get("/env_data")
def env_data():
    return {
        "ws_url": settings.ws_url,
        "python_version": f'{sys.version_info.major}.{sys.version_info.minor}',
        "zt_version": pkg_resources.get_distribution('zero-true').version
    }

@router.get("/base_path")
def base_path():
    return settings.user_name + '/' + settings.project_name

@router.websocket("/ws/run_code")
async def run_code(websocket: WebSocket):
    global current_thread
    if(run_mode=='dev'):
        message_send = asyncio.create_task(websocket_message_sender(notebook_state))
        await manager.connect(websocket)
        try:
            while True:
                data = await websocket.receive_json()
                ws_request = request.Request(**data)
                notebook_state.websocket = websocket
                current_thread = KThread(target = execute_request, args=(ws_request, notebook_state))
                current_thread.start()
        except WebSocketDisconnect:
            manager.disconnect(websocket)
        finally:
            message_send.cancel() 

@router.websocket("/ws/component_run")
async def component_run(websocket: WebSocket):
    global current_thread
    global user_threads
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            logger.debug("Component change code execution started")
            notebook = get_notebook_request()
            component_request = request.ComponentRequest(**data)
            cells = []
            for cell_key, cell in notebook.cells.items():
                cell_request=request.CodeRequest(
                    id=cell.id, 
                    code=cell.code,
                    variable_name=cell.variable_name,
                    nonReactive=cell.nonReactive,
                    cellType=cell.cellType
                )
                cells.append(cell_request)
            code_request = request.Request(
                originId=component_request.originId,
                cells=cells,
                components=component_request.components
            )
            if(run_mode=='dev'):
                notebook_state.websocket = websocket
                current_thread = KThread(target = execute_request, args=(code_request, notebook_state))
                current_thread.start()
            else:
                if component_request.userId not in user_states:
                    logger.debug("New user execution with id: %s, sending refresh", component_request.userId)
                    await websocket.send_json({"refresh": True})
                logger.debug("Existing user execution with id: %s", component_request.userId)
                timer_set(component_request.userId, 1800)
                user_states[component_request.userId].websocket = websocket
                user_threads[component_request.userId] = KThread(target = execute_request, args=(code_request, user_states[component_request.userId]))
                user_threads[component_request.userId].start()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.post("/api/create_cell")
def create_cell(cellRequest: request.CreateRequest):
     if(run_mode=='dev'):
        logger.debug("Code cell addition request started")
        createdCell = notebook.CodeCell(
            id=str(uuid.uuid4()),
            code='',
            components=[],
            output='',
            variable_name='',
            cellType=cellRequest.cellType
        )
        save_queue.put_nowait({"newCell": createdCell.model_copy(deep=True), "position_key":cellRequest.position_key})
        logger.debug("Code cell addition request completed")
        return createdCell

@router.post("/api/delete_cell")
def delete_cell(deleteRequest: request.DeleteRequest):
     cell_id = deleteRequest.cellId
     if(run_mode=='dev'):
        try:
            notebook_state.cell_outputs_dict.pop(cell_id, None)
        except Exception as e:
            logger.error("Error when deleting cell %s from cell_outputs_dict: %s", cell_id, traceback.format_exc())
        try:
            cell_dict = notebook_state.cell_outputs_dict['previous_dependecy_graph'].cells
            if cell_id in cell_dict:
                cell_dict.pop(cell_id, None)

            # Recursively search for and remove the cell ID from child_cells and parent_cells in other cells
            for cell_key, cell in cell_dict.items():
                if cell_id in dict(cell).get("child_cells", []):
                    cell["child_cells"].pop(cell_id, None)
                if cell_id in dict(cell).get("parent_cells", []):
                    cell["parent_cells"].pop(cell_id, None)

        except Exception as e:
            logger.debug("Error when deleting cell %s from cell dicts: %s", cell_id, traceback.format_exc())
        logger.debug("Cell %s deleted successfully", cell_id)
        save_queue.put_nowait({"deletedCell":cell_id})

@router.post("/api/hide_cell")
def hide_cell(hideCellRequest: request.HideCellRequest):
     if(run_mode=='dev'):
        logger.debug("Hide cell request started")
        save_queue.put_nowait({"hideCell": hideCellRequest})
        logger.debug("Hide cell request completed")

@router.post("/api/hide_code")
def hide_cell(hideCodeRequest: request.HideCodeRequest):
     if(run_mode=='dev'):
        logger.debug("Hide code request started")
        save_queue.put_nowait({"hideCode": hideCodeRequest})
        logger.debug("Hide code request completed")

@router.post("/api/rename_cell")
def rename_cell(renameCellRequest: request.NameCellRequest):
     if(run_mode=='dev'):
        logger.debug("Rename cell request started")
        save_queue.put_nowait({"renameCell": renameCellRequest})
        logger.debug("Rename cell request completed")

@router.post("/api/cell_reactivity")
def cell_reactivity(cellReactivityRequest: request.CellReactivityRequest):
     if(run_mode=='dev'):
        logger.debug("Rename cell request started")
        save_queue.put_nowait({"cellReactivity": cellReactivityRequest})
        logger.debug("Rename cell request completed")

@router.post("/api/expand_code")
def expand_code(expandCodeRequest: request.ExpandCodeRequest):
     if(run_mode=='dev'):
        logger.debug("Rename cell request started")
        save_queue.put_nowait({"expandCode": expandCodeRequest})
        logger.debug("Rename cell request completed")

@router.websocket("/ws/save_text")
async def save_text(websocket: WebSocket):
    if(run_mode=='dev'):
        save_task = asyncio.create_task(save_worker(save_queue))
        await manager.connect(websocket)
        try:
            while True:
                data = await websocket.receive_json()
                cell_type = data.get("cellType")
                code = data.get("text")
                cell_id = data.get("id")
                save_request = request.SaveRequest(id=cell_id, text=code, cellType=cell_type)
                save_queue.put_nowait({"saveCell":save_request})
                if cell_type=="code":
                    line = data.get("line")
                    column = data.get("column")
                    await text_document_did_change({
                        "textDocument": {
                            "uri": "file:///notebook.ztnb",
                            "version": 1
                        },
                        "contentChanges": [{
                            "text": data.get("code_w_context")
                        }]
                    })
                    code_w_context= data.get("code_w_context")
                    completions = get_code_completions(cell_id, code_w_context, line, column)
                    await websocket.send_json(completions)
        except WebSocketDisconnect:
            manager.disconnect(websocket)
        finally:
            save_task.cancel()

@router.post("/api/clear_state")
def clear_state(clearRequest: request.ClearRequest):
     if(run_mode=='app'):
        logger.debug("Clearing state for user %s", clearRequest.userId)
        user_states.pop(clearRequest.userId, None)

@router.post("/api/dependency_update")
def dependency_update(dependencyRequest: request.DependencyRequest):
     if(run_mode=='dev'):
        logger.debug("Updating dependencies")
        try:
            with open('requirements.txt', 'r+', encoding='utf-8') as file:
                contents = file.read()
                if contents == dependencyRequest.dependencies:
                    return "No change to dependencies"
                file.seek(0)
                file.write(dependencyRequest.dependencies)
                file.truncate()
                subprocess.run(['pip', 'install', '-r', 'requirements.txt'])
                subprocess.run(['lock', 'requirements.txt'])
                logger.debug("Successfully updated dependencies")
        except Exception as e:
            logger.error('Error while updating requirements: %s', traceback.format_exc())

@router.websocket("/ws/notebook")
async def load_notebook(websocket: WebSocket):
    global user_threads
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
            logger.debug("Get notebook request received")
            notebook_start = get_notebook_request()
            await websocket.send_json({"notebook_name": notebook_start.notebookName})
            if (run_mode=='app'):
                userId = str(uuid.uuid4())
                notebook_start.userId = userId
                user_states[userId]=UserState(userId)
                user_message_tasks[userId]=asyncio.create_task(websocket_message_sender(user_states[userId]))
                timer_set(userId, 1800)
                cells = []
                components={}

                for cell_key, cell in notebook_start.cells.items():
                    cell_request=request.CodeRequest(
                        id=cell.id, 
                        code=cell.code,
                        variable_name=cell.variable_name,
                        nonReactive=cell.nonReactive,
                        cellType=cell.cellType
                    )
                    for comp in cell.components:
                        if hasattr(comp, 'value'):
                            components[comp.id] = comp.value
                    cells.append(cell_request)
                code_request = request.Request(
                    originId='',
                    cells=cells,
                    components=components
                )
                notebook_response = notebook.NotebookResponse(notebook=notebook_start, dependencies=notebook.Dependencies(value=''))
                await websocket.send_json(notebook_response.model_dump_json())
                user_states[userId].websocket = websocket
                user_threads[userId] = KThread(target = execute_request, args=(code_request, user_states[userId]))
                user_threads[userId].start()
            else:
                try:
                    with open('requirements.txt', 'r', encoding='utf-8') as file:
                        contents = file.read()
                    notebook_response =  notebook.NotebookResponse(notebook=notebook_start, dependencies=notebook.Dependencies(value=contents))
                    await websocket.send_json(notebook_response.model_dump_json())
                    await websocket.send_json({"complete": True})
                except FileNotFoundError:
                    logger.error('Requirements file not found')

    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.websocket("/ws/stop_execution")
async def stop_execution(websocket: WebSocket):
    global current_thread
    global user_threads
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if run_mode=='dev' and current_thread:
                current_thread.kill()
                notebook_state.current_cell_components.clear()
                notebook_state.current_cell_layout.clear()
                notebook_state.component_values.clear()
                notebook_state.created_components.clear()
                notebook_state.context_globals['exec_mode'] = False
            if run_mode=='app' and user_threads[data]:
                user_threads[data].kill()
                user_states[data].current_cell_components.clear()
                user_states[data].current_cell_layout.clear()
                user_states[data].component_values.clear()
                user_states[data].created_components.clear()
                user_states[data].context_globals['exec_mode'] = False
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.post("/api/notebook_name_update")
def notebook_name_update(notebook_name: request.NotebookNameRequest):
    if(run_mode=='dev'):
        save_queue.put_nowait({"new_notebook_name":notebook_name.notebookName})

@router.on_event('shutdown')
def shutdown():
    global current_thread
    global user_threads
    if current_thread:
        current_thread.kill()
    for user_id in user_threads:
        if user_threads[user_id]:
            user_threads[user_id].kill()
    for user_id in user_timers:
        if user_timers[user_id]:
            user_timers[user_id].cancel()
    for user_id in user_message_tasks:
        if user_message_tasks[user_id]:
            user_message_tasks[user_id].cancel()

def remove_user_state(user_id):
    try:
        if user_id in user_timers:
            # Cancel and remove the associated timer
            timer = user_timers[user_id]
            message_sender = user_message_tasks[user_id]
            if timer:
                timer.cancel()
            del user_timers[user_id]
            if message_sender:
                message_sender.cancel() 
            del user_message_tasks[user_id]
            if user_id in user_states: del user_states[user_id]
            logger.debug("User state removed for user %s", user_id)
    except Exception as e:
        logger.error("Error removing user state for user %s: %s", user_id, traceback.format_exc())

def timer_set(user_id, timeout_seconds):
    logger.debug("Starting timer for user %s", user_id)
    if user_id in user_timers:
        existing_timer = user_timers[user_id]
        if existing_timer:
            existing_timer.cancel()
        
        timer = threading.Timer(timeout_seconds, remove_user_state, args=(user_id,))
        timer.daemon=True
        timer.start()
        
        user_timers[user_id] = timer
