import shutil
from fastapi import (
    APIRouter,
    Depends,
    WebSocket,
    WebSocketDisconnect,
    Query,
    UploadFile,
    File,
    Form,
    HTTPException,
    status,
    BackgroundTasks,
)
from zt_backend.models import notebook
from zt_backend.models.api import request
from zt_backend.runner.execute_code import execute_request
from zt_backend.config import settings
from zt_backend.utils.completions import get_code_completions
from zt_backend.utils.linting import queued_get_cell_linting
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
from zt_backend.models.state.notebook_state import UploadState
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.requests import Request
from pathlib import Path
import logging
import uuid
import os
import traceback
import sys
import asyncio
import pkg_resources
import requests
import re
from zt_backend.utils.file_utils import upload_queue
from typing import Optional
import mimetypes
from typing import Dict, Tuple, Optional
import aiofiles
import tempfile
from zt_backend.utils.file_utils import *


router = APIRouter()
manager = ConnectionManager()
current_path = os.path.dirname(os.path.abspath(__file__))
app_state = AppState()
upload_state = UploadState(None)

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
    environment_data = {
        "ws_url": settings.ws_url,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
        "zt_version": pkg_resources.get_distribution("zero-true").version,
        "comments_enabled": settings.comments_enabled,
        "show_create_button": settings.show_create_button,
    }
    if settings.user_name:
        environment_data["user_name"] = settings.user_name
    if settings.project_name:
        environment_data["project_name"] = settings.project_name
    if settings.team_name:
        environment_data["team_name"] = settings.team_name
    return environment_data


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


@router.post("/api/run_all")
def run_all():
    if app_state.run_mode == "app":
        run_thread = KThread(
            target=execute_request,
            args=(get_request_base(""), UserState(str(uuid.uuid4()))),
        )
        run_thread.start()


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
                        try:
                            completions = await get_code_completions(
                                cell_id,
                                data.get("code_w_context"),
                                data.get("line"),
                                data.get("column"),
                            )

                            await queued_get_cell_linting(
                                cell_id,
                                data.get("text"),
                                data.get("code_w_context"),
                                websocket,
                            )

                            combined_results = {
                                "cell_id": cell_id,
                                "completions": completions.get("completions", []),
                            }

                            await websocket.send_json(combined_results)

                        except Exception as e:
                            logger.error(
                                f"Error processing code cell {cell_id}: {str(e)}"
                            )
                            await websocket.send_json(
                                {
                                    "cell_id": cell_id,
                                    "error": "An error occurred while processing the code cell",
                                }
                            )
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
    try:
        if app_state.run_mode == "dev":
            headers = {
                "Content-Type": "application/json",
                "x-api-key": shareRequest.apiKey,
            }
            user_name = shareRequest.userName.lower().strip()
            project_name = shareRequest.projectName.lower().strip()
            compute_profile_long = shareRequest.computeProfile.strip()
            python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
            zt_version = pkg_resources.get_distribution("zero-true").version
            if compute_profile_long == "Small (1 CPU, 4GB RAM)":
                compute_profile = "small"
            elif compute_profile_long == "Medium (1.5 CPU, 8GB RAM)":
                compute_profile = "medium"
            elif compute_profile_long == "Large (2 CPU, 16GB RAM)":
                compute_profile = "large"
            elif compute_profile_long == "X-Large (4 CPU, 32GB RAM)":
                compute_profile = "xlarge"
            else:
                compute_profile = "xsmall"
            if shareRequest.teamName:
                team_name = re.sub(r"\s+", "-", shareRequest.teamName.lower().strip())
                s3_key = team_name + "/" + project_name + "/" + project_name + ".tar.gz"
                response = requests.post(
                    settings.publish_url + "team_project_upload",
                    json={
                        "s3_key": s3_key,
                        "user_name": user_name,
                        "python_version": python_version,
                        "zero_true_version": zt_version,
                        "compute_profile": compute_profile,
                        "private": True,
                    },
                    headers=headers,
                )
            else:
                if compute_profile not in ["xsmall", "small", "medium"]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid compute profile for individual project",
                    )
                s3_key = user_name + "/" + project_name + "/" + project_name + ".tar.gz"
                response = requests.post(
                    settings.publish_url + "project_upload",
                    json={
                        "s3_key": s3_key,
                        "python_version": python_version,
                        "zero_true_version": zt_version,
                        "compute_profile": compute_profile,
                        "private": False,
                    },
                    headers=headers,
                )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get(
                        "message",
                        response.json().get("Message", "Failed to get signed URL"),
                    ),
                )

            response_json = response.json()
            signed_url = response_json.get("uploadURL")
            if not signed_url:
                return {"Error": "Failed to get signed URL"}

            output_filename = f"{project_name}"
            project_source = os.path.normpath(os.getcwd())
            logger.info(project_source)
            shutil.make_archive(
                base_name=output_filename, format="gztar", root_dir=project_source
            )

        with output_filename.open("rb") as file:
            upload_files = {"file": file}
            upload_response = requests.post(
                signed_url["url"], data=signed_url["fields"], files=upload_files
            )

        if upload_response.status_code != 204:
            return {
                "Error": upload_response.json().get(
                    "message",
                    upload_response.json().get("Message", "Failed to upload files"),
                )
            }

        try:
            output_filename.unlink()
        except OSError as e:
            logger.warning(f"Failed to remove temporary file: {e}")
            try:
                output_filename.unlink()
            except OSError as e:
                logger.error(f"Failed to remove temporary file after retry: {e}")

    except Exception as e:
        try:
            if output_filename.exists():
                output_filename.unlink()
        except OSError:
            pass
        raise e

@router.post("/api/upload_file")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    chunk_index: int = Form(...),
    total_chunks: int = Form(...),
    path: str = Form(...),
    file_name: str = Form(...),
    is_folder: bool = Form(False),
    relative_path: Optional[str] = Form(None)
):
    if app_state.run_mode == "dev":
        """
        Handle file upload with queuing mechanism and existence validation
        """
        try:
            final_path = relative_path if relative_path else file_name
            full_path = Path(path) / final_path

            # Check for existing file/folder on first chunk
            if chunk_index == 0:
                if full_path.exists():
                    raise HTTPException(
                        status_code=409,  # Conflict status code
                        detail=f"{'Folder' if is_folder else 'File'} already exists: {final_path}"
                    )

                can_queue = await upload_queue.add_to_queue(final_path, total_chunks)
                if not can_queue:
                    raise HTTPException(
                        status_code=503,
                        detail="Server busy: Maximum queue size reached"
                    )

            # Process chunk
            chunk_data = await file.read()
            result = await upload_queue.process_chunk(
                final_path, chunk_index, chunk_data, path
            )
            return result

        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/api/create_item")
def create_item(item: request.CreateItemRequest):
    if app_state.run_mode == "dev":
        try:
            full_path = Path(item.path) / item.name

            if full_path.exists():
                raise HTTPException(status_code=400, detail="Item already exists")

            if item.type == "folder":
                full_path.mkdir(parents=True, exist_ok=True)
            elif item.type == "file":
                full_path.touch()
            else:
                raise HTTPException(status_code=400, detail="Invalid item type")

            return {
                "success": True,
                "message": f"{item.type.capitalize()} created successfully",
                "path": str(full_path),
            }
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to create {item.type}: {str(e)}"
            )


@router.post("/api/rename_item")
async def rename_item(request: request.RenameItemRequest):
    if app_state.run_mode == "dev":
        try:
            # Convert to Path object and resolve to absolute path
            base_path = Path(request.path).resolve()
            
            # Construct the full old path
            # Don't append oldName if it's already part of the path
            if base_path.name != request.oldName:
                old_path = base_path / request.oldName
            else:
                old_path = base_path
                
            # Construct the new path in the same directory
            new_path = old_path.parent / request.newName
            
            # Validate paths
            if not old_path.exists():
                raise FileNotFoundError(f"The file {old_path} does not exist")
                
            if new_path.exists():
                raise FileExistsError(f"The destination {new_path} already exists")
                
            # Perform renaming
            old_path.rename(new_path)
            
            logging.info(f"Successfully renamed {old_path} to {new_path}")
            return {"success": True, "message": "File renamed successfully"}
            
        except Exception as e:
            error_msg = f"Error renaming file: {str(e)}"
            logging.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)
    
@router.post("/api/delete_item")
def delete_item(delete_request: request.DeleteItemRequest):
    if app_state.run_mode == "dev":
        try:
            # Clean the input path
            file_path = delete_request.path.strip("/")
            
            
            # Get base path and construct full path
            base_path = Path(".").resolve()
            item_path = (base_path / file_path).resolve()
                
            # Security check
            try:
                item_path.relative_to(base_path)
            except ValueError:
                raise HTTPException(
                    status_code=403,
                    detail="Access denied: Cannot delete items outside base directory"
                )

            if not item_path.exists():
                raise HTTPException(
                    status_code=404,
                    detail=f"Item not found: {file_path}"
                )

            if item_path.is_file():
                os.remove(item_path)
            elif item_path.is_dir():
                shutil.rmtree(item_path)
            else:
                raise HTTPException(status_code=400, detail="Invalid item type")

            return {
                "success": True,
                "message": "Item deleted successfully",
                "deletedPath": str(item_path.relative_to(base_path))
            }
        except PermissionError:
            raise HTTPException(
                status_code=403,
                detail="Permission denied. Unable to delete the item."
            )
        except OSError as e:
            raise HTTPException(status_code=500, detail=f"System error: {str(e)}")
        except Exception as e:
            logging.exception("Unexpected error in delete_item")
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred: {str(e)}"
            )


@router.get("/api/read_file")
def read_file(path: str):
    if app_state.run_mode == "dev":
        try:
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            return {"content": content}
        
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail="The type of file you are trying to edit cannot be edited. Please ensure you edit a compatible file."
            )
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="File not found")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/write_file")
def write_file(file_data: request.FileWrite):
    if app_state.run_mode == "dev":
        try:
            # Convert to Path object and normalize
            file_path = Path(file_data.path).resolve()\
                    
            # Get the base directory where files should be stored
            base_dir = Path.cwd()
            
            # Ensure the file path is within the base directory (prevent path traversal)
            if not str(file_path).startswith(str(base_dir)):
                raise HTTPException(status_code=400, detail="Invalid path: path must be within base directory")
                
            # Get directory name using pathlib
            dir_path = file_path.parent
            
            # Create directories only if necessary
            if dir_path != base_dir:
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                except OSError as e:
                    raise HTTPException(status_code=500, detail=f"Failed to create directory: {str(e)}")
            
            # Write the file
            try:
                mode = "a" if file_data.chunk_index > 0 else "w"
                with open(file_path, mode, encoding="utf-8") as f:
                    f.write(file_data.content)
            except IOError as e:
                raise HTTPException(status_code=500, detail=f"Failed to write file: {str(e)}")
                
            return {
                "message": "File saved successfully",
                "path": str(file_path.relative_to(base_dir))
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/download")
async def download_item(
    request: Request,
    background_tasks: BackgroundTasks,  # Add this parameter
    download_req: request.DownloadRequest = Depends()
):
    if app_state.run_mode == "dev":
        """Stream download with range support for files and folders."""
        temp_zip_path = None  # Define this outside try block to use in cleanup
        
        try:
            chunk_size: int = 8192
            file_path = Path(download_req.path).resolve()
            
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="Path not found")

            if download_req.isFolder:
                # Create temporary zip file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
                temp_zip_path = temp_file.name
                temp_file.close()  # Close the file handle
                
                await create_zip_file(file_path, temp_zip_path)
                file_path = Path(temp_zip_path)
                download_req.filename = f"{download_req.filename}.zip"

            file_size = file_path.stat().st_size
            start, end = await parse_range_header(
                request.headers.get('range'),
                file_size
            )

            # Define cleanup function
            def cleanup_temp_file():
                if temp_zip_path and os.path.exists(temp_zip_path):
                    try:
                        os.unlink(temp_zip_path)
                    except Exception as e:
                        print(f"Error cleaning up temp file: {e}")

            # Add cleanup to background tasks if we created a zip
            if download_req.isFolder:
                background_tasks.add_task(cleanup_temp_file)

            response = StreamingResponse(
                stream_file_range(str(file_path), start, end, chunk_size),
                status_code=206 if request.headers.get('range') else 200,
                media_type=get_mime_type(download_req.filename)
            )

            response.headers.update({
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Content-Length": str(end - start + 1),
                "Content-Disposition": f"attachment; filename={download_req.filename}",
                "Accept-Ranges": "bytes"
            })

            return response

        except Exception as e:
            # Cleanup temp file if something goes wrong
            if temp_zip_path and os.path.exists(temp_zip_path):
                try:
                    os.unlink(temp_zip_path)
                except Exception:
                    pass  # If cleanup fails during error handling, just continue
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )

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
    if settings.comments_enabled:
        app_state.save_queue.put_nowait({"add_comment": comment})


@router.post("/api/delete_comment")
def delete_comment(comment: request.DeleteCommentRequest):
    if settings.comments_enabled:
        app_state.save_queue.put_nowait({"delete_comment": comment})


@router.post("/api/edit_comment")
def edit_comment(comment: request.EditCommentRequest):
    if settings.comments_enabled:
        app_state.save_queue.put_nowait({"edit_comment": comment})


@router.post("/api/resolve_comment")
def resolve_comment(comment: request.ResolveCommentRequest):
    if settings.comments_enabled:
        app_state.save_queue.put_nowait({"resolve_comment": comment})


@router.post("/api/add_reply")
def add_reply(reply: request.AddReplyRequest):
    if settings.comments_enabled:
        app_state.save_queue.put_nowait({"add_reply": reply})


@router.post("/api/delete_reply")
def delete_reply(reply: request.DeleteReplyRequest):
    if settings.comments_enabled:
        app_state.save_queue.put_nowait({"delete_reply": reply})


@router.post("/api/edit_reply")
def edit_reply(reply: request.EditReplyRequest):
    if settings.comments_enabled:
        app_state.save_queue.put_nowait({"edit_reply": reply})


@router.on_event("shutdown")
def shutdown():
    app_state.shutdown()
