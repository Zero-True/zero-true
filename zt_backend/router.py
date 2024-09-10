import subprocess
from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    Query,
    UploadFile,
    File,
    Form,
)
from zt_backend.models import notebook
from zt_backend.models.api import request
from zt_backend.runner.execute_code import execute_request
from zt_backend.config import settings
from zt_backend.utils.completions import get_code_completions
from zt_backend.utils.dependencies import (
    dependency_update,
    parse_dependencies,
    check_env,
)
from zt_backend.utils.notebook import (
    get_notebook_request,
    get_request_base,
    save_worker,
    websocket_message_sender,
)
from zt_backend.models.managers.connection_manager import ConnectionManager
from zt_backend.models.managers.k_thread import KThread
from zt_backend.models.state.user_state import UserState
from zt_backend.models.state.app_state import AppState
from fastapi.responses import HTMLResponse
from pathlib import Path
import logging
import uuid
import os
import traceback
import sys
import asyncio
import pkg_resources

router = APIRouter()
manager = ConnectionManager()
current_path = os.path.dirname(os.path.abspath(__file__))
app_state = AppState()

logger = logging.getLogger("__name__")


@router.get("/app", response_class=HTMLResponse)
async def catch_all():
    if app_state.run_mode == "dev":
        return HTMLResponse(
            open(os.path.join(current_path, "dist_dev", "index.html")).read()
        )


@router.get("/health")
def health():
    return "UP"


@router.get("/env_data")
def env_data():
    return {
        "ws_url": settings.ws_url,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
        "zt_version": pkg_resources.get_distribution("zero-true").version,
    }


@router.get("/base_path")
def base_path():
    return settings.user_name + "/" + settings.project_name


@router.websocket("/ws/run_code")
async def run_code(websocket: WebSocket):
    if app_state.run_mode == "dev":
        message_send = asyncio.create_task(
            websocket_message_sender(app_state.notebook_state)
        )
        await manager.connect(websocket)
        try:
            while True:
                data = await websocket.receive_json()
                if data.get("type", "") == "ping":
                    await websocket.send_text("pong")
                else:
                    app_state.notebook_state.websocket = websocket
                    app_state.current_thread = KThread(
                        target=execute_request,
                        args=(request.Request(**data), app_state.notebook_state),
                    )
                    app_state.current_thread.start()
        except WebSocketDisconnect:
            manager.disconnect(websocket)
        finally:
            message_send.cancel()


@router.websocket("/ws/component_run")
async def component_run(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type", "") == "ping":
                await websocket.send_text("pong")
            else:
                logger.debug("Component change code execution started")
                component_request = request.ComponentRequest(**data)
                code_request = get_request_base(
                    component_request.originId, component_request.components
                )
                if app_state.run_mode == "dev":
                    app_state.notebook_state.websocket = websocket
                    current_thread = KThread(
                        target=execute_request,
                        args=(code_request, app_state.notebook_state),
                    )
                    current_thread.start()
                else:
                    if component_request.userId not in app_state.user_states:
                        logger.debug(
                            "New user execution with id: %s, sending refresh",
                            component_request.userId,
                        )
                        await websocket.send_json({"refresh": True})
                    logger.debug(
                        "Existing user execution with id: %s", component_request.userId
                    )
                    app_state.timer_set(component_request.userId, 1800)
                    app_state.user_states[component_request.userId].websocket = (
                        websocket
                    )
                    app_state.user_threads[component_request.userId] = KThread(
                        target=execute_request,
                        args=(
                            code_request,
                            app_state.user_states[component_request.userId],
                        ),
                    )
                    app_state.user_threads[component_request.userId].start()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.post("/api/create_cell")
def create_cell(cellRequest: request.CreateRequest):
    if app_state.run_mode == "dev":
        logger.debug("Code cell addition request started")
        createdCell = notebook.CodeCell(
            id=str(uuid.uuid4()),
            code="",
            components=[],
            output="",
            variable_name="",
            cellType=cellRequest.cellType,
        )
        app_state.save_queue.put_nowait(
            {
                "newCell": createdCell.model_copy(deep=True),
                "position_key": cellRequest.position_key,
            }
        )
        logger.debug("Code cell addition request completed")
        return createdCell


@router.post("/api/delete_cell")
def delete_cell(deleteRequest: request.DeleteRequest):
    cell_id = deleteRequest.cellId
    if app_state.run_mode == "dev":
        app_state.notebook_state.cell_outputs_dict.pop(cell_id, None)
        try:
            cell_dict = app_state.notebook_state.cell_outputs_dict[
                "previous_dependecy_graph"
            ].cells
            if cell_id in cell_dict:
                cell_dict.pop(cell_id, None)

            for cell_key, cell in cell_dict.items():
                if cell_id in dict(cell).get("child_cells", []):
                    cell["child_cells"].pop(cell_id, None)
                if cell_id in dict(cell).get("parent_cells", []):
                    cell["parent_cells"].pop(cell_id, None)

            logger.debug("Cell %s deleted successfully", cell_id)
        except Exception as e:
            logger.debug(
                "Error when deleting cell %s: %s", cell_id, traceback.format_exc()
            )
        app_state.save_queue.put_nowait({"deletedCell": cell_id})


@router.post("/api/hide_cell")
def hide_cell(hideCellRequest: request.HideCellRequest):
    if app_state.run_mode == "dev":
        logger.debug("Hide cell request started")
        app_state.save_queue.put_nowait({"hideCell": hideCellRequest})
        logger.debug("Hide cell request completed")


@router.post("/api/hide_code")
def hide_cell(hideCodeRequest: request.HideCodeRequest):
    if app_state.run_mode == "dev":
        logger.debug("Hide code request started")
        app_state.save_queue.put_nowait({"hideCode": hideCodeRequest})
        logger.debug("Hide code request completed")


@router.post("/api/rename_cell")
def rename_cell(renameCellRequest: request.NameCellRequest):
    if app_state.run_mode == "dev":
        logger.debug("Rename cell request started")
        app_state.save_queue.put_nowait({"renameCell": renameCellRequest})
        logger.debug("Rename cell request completed")


@router.post("/api/cell_reactivity")
def cell_reactivity(cellReactivityRequest: request.CellReactivityRequest):
    if app_state.run_mode == "dev":
        logger.debug("Cell reactivity request started")
        app_state.save_queue.put_nowait({"cellReactivity": cellReactivityRequest})
        logger.debug("Cell reactivity request completed")


@router.post("/api/expand_code")
def expand_code(expandCodeRequest: request.ExpandCodeRequest):
    if app_state.run_mode == "dev":
        logger.debug("Expand code request started")
        app_state.save_queue.put_nowait({"expandCode": expandCodeRequest})
        logger.debug("Expand code request completed")


@router.post("/api/show_table")
def show_table(showTableRequest: request.ShowTableRequest):
    if app_state.run_mode == "dev":
        logger.debug("Show Table request started")
        app_state.save_queue.put_nowait({"showTable": showTableRequest})
        logger.debug("Show Table request completed")


@router.websocket("/ws/save_text")
async def save_text(websocket: WebSocket):
    if app_state.run_mode == "dev":
        save_task = asyncio.create_task(save_worker(app_state.save_queue))
        await manager.connect(websocket)
        try:
            while True:
                data = await websocket.receive_json()
                if data.get("type", "") == "ping":
                    await websocket.send_text("pong")
                else:
                    cell_type = data.get("cellType")
                    cell_id = data.get("id")
                    app_state.save_queue.put_nowait(
                        {
                            "saveCell": request.SaveRequest(
                                id=cell_id, text=data.get("text"), cellType=cell_type
                            )
                        }
                    )
                    if cell_type == "code":
                        completions = await get_code_completions(
                            cell_id,
                            data.get("code_w_context"),
                            data.get("line"),
                            data.get("column"),
                        )
                        await websocket.send_json(completions)
        except WebSocketDisconnect:
            manager.disconnect(websocket)
        finally:
            save_task.cancel()


@router.post("/api/clear_state")
def clear_state(clearRequest: request.ClearRequest):
    if app_state.run_mode == "app":
        logger.debug("Clearing state for user %s", clearRequest.userId)
        app_state.user_states.pop(clearRequest.userId, None)


@router.websocket("/ws/dependency_update")
async def dependency_update_request(websocket: WebSocket):
    if app_state.run_mode == "dev":
        await manager.connect(websocket)
        try:
            while True:
                data = await websocket.receive_json()
                if data.get("type", "") == "ping":
                    await websocket.send_text("pong")
                else:
                    dependencyRequest = request.DependencyRequest(**data)
                    dependencyResponse = await dependency_update(
                        dependencyRequest, websocket
                    )
                    await websocket.send_json(dependencyResponse.model_dump_json())
        except WebSocketDisconnect:
            manager.disconnect(websocket)


@router.websocket("/ws/notebook")
async def load_notebook(websocket: WebSocket):
    await manager.connect(websocket)
    if app_state.run_mode == "app":
        save_task = asyncio.create_task(save_worker(app_state.save_queue))
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type", "") == "ping":
                await websocket.send_text("pong")
            else:
                logger.debug("Get notebook request received")
                notebook_start = get_notebook_request()
                await websocket.send_json(
                    {"notebook_name": notebook_start.notebookName}
                )
                if app_state.run_mode == "app":
                    userId = str(uuid.uuid4())
                    notebook_start.userId = userId
                    app_state.user_states[userId] = UserState(userId)
                    app_state.user_message_tasks[userId] = asyncio.create_task(
                        websocket_message_sender(app_state.user_states[userId])
                    )
                    app_state.timer_set(userId, 1800)
                    notebook_response = notebook.NotebookResponse(
                        notebook=notebook_start,
                        dependencies=notebook.Dependencies(value=""),
                    )
                    await websocket.send_json(notebook_response.model_dump_json())
                    app_state.user_states[userId].websocket = websocket
                    app_state.user_threads[userId] = KThread(
                        target=execute_request,
                        args=(get_request_base(""), app_state.user_states[userId]),
                    )
                    app_state.user_threads[userId].start()
                else:
                    try:
                        start_dependencies = parse_dependencies()
                        if not check_env(start_dependencies):
                            await websocket.send_json({"env_stale": True})
                        notebook_response = notebook.NotebookResponse(
                            notebook=notebook_start, dependencies=start_dependencies
                        )
                        await websocket.send_json(notebook_response.model_dump_json())
                        app_state.notebook_state.websocket = websocket
                        app_state.current_thread = KThread(
                            target=execute_request,
                            args=(
                                get_request_base("initial_cell"),
                                app_state.notebook_state,
                            ),
                        )
                        app_state.current_thread.start()
                        await websocket.send_json({"complete": True})
                    except FileNotFoundError:
                        logger.error("Requirements file not found")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    finally:
        if app_state.run_mode == "app":
            save_task.cancel()


@router.websocket("/ws/stop_execution")
async def stop_execution(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type", "") == "ping":
                await websocket.send_text("pong")
            else:
                app_state.stop_execution(data.get("userId"))
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.post("/api/notebook_name_update")
def notebook_name_update(notebook_name: request.NotebookNameRequest):
    if app_state.run_mode == "dev":
        app_state.save_queue.put_nowait(
            {"new_notebook_name": notebook_name.notebookName}
        )


@router.post("/api/share_notebook")
def share_notebook(shareRequest: request.ShareRequest):
    if app_state.run_mode == "dev":
        if shareRequest.teamName:
            subprocess.run(
                [
                    "zero-true",
                    "publish",
                    shareRequest.apiKey,
                    shareRequest.userName,
                    shareRequest.projectName,
                    ".",
                    shareRequest.teamName,
                ]
            )
        else:
            subprocess.run(
                [
                    "zero-true",
                    "publish",
                    shareRequest.apiKey,
                    shareRequest.userName,
                    shareRequest.projectName,
                    ".",
                ]
            )


@router.post("/api/upload_file")
async def upload_file(file: UploadFile = File(...), path: str = Form(...)):
    if app_state.run_mode == "dev":
        logger.debug("File upload request started")

        # Ensure the path exists
        os.makedirs(path, exist_ok=True)

        file_path = os.path.join(path, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        logger.debug(f"File upload request completed. File saved to: {file_path}")
        return {"filename": file.filename, "path": file_path}


def get_file_type(name):
    extension = name.split(".")[-1]
    if extension in ["html", "js", "json", "md", "pdf", "png", "txt", "xls"]:
        return extension
    return None


def list_dir(path):
    items = []
    for item in path.iterdir():
        if item.is_dir():
            items.append(
                {
                    "title": item.name,
                    "file": "folder",
                    "id": item.as_posix(),
                    "children": [],
                }
            )
        else:
            file_type = get_file_type(item.name)
            if file_type:
                items.append(
                    {"title": item.name, "file": file_type, "id": item.as_posix()}
                )
            else:
                items.append(
                    {"title": item.name, "file": "file", "id": item.as_posix()}
                )
    return items


@router.get("/api/get_files")
def list_files():
    path = Path(".")
    files = list_dir(path)
    return {"files": files}


@router.get("/api/get_children")
def list_children(path: str = Query(...)):
    dir_path = Path(path)
    if not dir_path.is_dir():
        return {"error": "Path is not a directory"}

    items = list_dir(dir_path)
    return {"files": items}


@router.post("/api/add_comment")
def add_comment(comment: request.AddCommentRequest):
    app_state.save_queue.put_nowait({"add_comment": comment})


@router.post("/api/delete_comment")
def delete_comment(comment: request.DeleteCommentRequest):
    app_state.save_queue.put_nowait({"delete_comment": comment})


@router.post("/api/edit_comment")
def edit_comment(comment: request.EditCommentRequest):
    app_state.save_queue.put_nowait({"edit_comment": comment})


@router.post("/api/resolve_comment")
def resolve_comment(comment: request.ResolveCommentRequest):
    app_state.save_queue.put_nowait({"resolve_comment": comment})


@router.post("/api/add_reply")
def add_reply(reply: request.AddReplyRequest):
    app_state.save_queue.put_nowait({"add_reply": reply})


@router.post("/api/delete_reply")
def delete_reply(reply: request.DeleteReplyRequest):
    app_state.save_queue.put_nowait({"delete_reply": reply})


@router.post("/api/edit_reply")
def edit_reply(reply: request.EditReplyRequest):
    app_state.save_queue.put_nowait({"edit_reply": reply})


@router.on_event("shutdown")
def shutdown():
    app_state.shutdown()
