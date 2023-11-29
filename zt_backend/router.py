import subprocess
from fastapi import APIRouter,BackgroundTasks
from typing import OrderedDict
from zt_backend.models import request, notebook, response
from zt_backend.runner.execute_code import execute_request
from zt_backend.config import settings
from dictdiffer import diff
import logging
import site 
import json
import duckdb
import uuid
import os
import toml
import threading
import traceback

router = APIRouter()

#connect to db for saving notebook
notebook_db_dir =  site.USER_SITE+'/.zero_true/'
notebook_db_path = notebook_db_dir+'notebook.db'
os.makedirs(notebook_db_dir, exist_ok=True)

conn = duckdb.connect(notebook_db_path)
# Create the table for the notebook
conn.execute('''
    CREATE TABLE IF NOT EXISTS notebooks (
        id STRING  PRIMARY KEY,
        notebook STRING
    )
''')
conn.close()
user_states={}
cell_outputs_dict={}
run_mode = settings.run_mode

logger = logging.getLogger("__name__")

@router.get("/health")
def health():
    return('UP')

@router.post("/api/runcode")
async def runcode(request: request.Request,background_tasks: BackgroundTasks):
    if(run_mode=='dev'):
        logger.debug("Code execution starting")
        background_tasks.add_task(globalStateUpdate,run_request=request.model_copy(deep=True))
        response = execute_request(request, cell_outputs_dict)
        background_tasks.add_task(globalStateUpdate,run_response=response)
        logger.debug("Code execution completed")
        return response

@router.post("/api/component_run")
def runcode(component_request: request.ComponentRequest):
    logger.debug("Component change code execution started")
    notebook = get_notebook()
    cells = []
    for cell_key, cell in notebook.cells.items():
        cell_request=request.CodeRequest(
            id=cell.id, 
            code=cell.code,
            variable_name=cell.variable_name,
            cellType=cell.cellType
        )
        cells.append(cell_request)
    code_request = request.Request(
        originId=component_request.originId,
        cells=cells,
        components=component_request.components
    )
    if(run_mode=='dev'):
        return execute_request(code_request, cell_outputs_dict)
    else:
        if component_request.userId not in user_states:
            logger.debug("New user execution with id: %s, sending refresh", component_request.userId)
            return response.Response(cells=[], refresh=True)
        logger.debug("Existing user execution with id: %s", component_request.userId)
        timer_set(component_request.userId, 1800)
        return execute_request(code_request, user_states[component_request.userId])



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
        globalStateUpdate(newCell=createdCell.model_copy(deep=True), position_key=cellRequest.position_key)
        logger.debug("Code cell addition request completed")
        return createdCell

@router.post("/api/delete_cell")
def delete_cell(deleteRequest: request.DeleteRequest):
     cell_id = deleteRequest.cellId
     if(run_mode=='dev'):
        try:
            cell_outputs_dict.pop(cell_id, None)
        except Exception as e:
            logger.error("Error when deleting cell %s from cell_outputs_dict: %s", cell_id, traceback.format_exc())
        try:
            cell_dict = cell_outputs_dict['previous_dependecy_graph'].cells
            if cell_id in cell_dict:
                cell_dict.pop(cell_id, None)

            # Recursively search for and remove the cell ID from child_cells and parent_cells in other cells
            for cell_key, cell in cell_dict.items():
                if cell_id in dict(cell).get("child_cells", []):
                    cell["child_cells"].pop(cell_id, None)
                if cell_id in dict(cell).get("parent_cells", []):
                    cell["parent_cells"].pop(cell_id, None)

        except Exception as e:
            logger.error("Error when deleting cell %s from cell dicts: %s", cell_id, traceback.format_exc())
        logger.debug("Cell %s deleted successfully", cell_id)
        globalStateUpdate(deletedCell=cell_id)

@router.post("/api/save_text")
def save_text(saveRequest: request.SaveRequest):
     if(run_mode=='dev'):
        logger.debug("Save cell request received")
        globalStateUpdate(saveCell=saveRequest)

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
                subprocess.run("pip install -r requirements.txt")
                subprocess.run("lock requirements.txt")
                logger.debug("Successfully updated dependencies")
        except Exception as e:
            logger.error('Error while updating requirements: %s', traceback.format_exc())

@router.get("/api/notebook")
def load_notebook():
    logger.debug("Get notebook request received")
    notebook_start = get_notebook()
    if (run_mode=='app'):
        userId = str(uuid.uuid4())
        notebook_start.userId = userId
        user_states[userId]={}
        timer_set(userId, 1800)
        cells = []
        components={}

        for cell_key, cell in notebook_start.cells.items():
            cell_request=request.CodeRequest(
                id=cell.id, 
                code=cell.code,
                variable_name=cell.variable_name,
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
        response = execute_request(code_request, user_states[userId])
        for responseCell in response.cells:
            notebook_start.cells[responseCell.id].components = responseCell.components
            notebook_start.cells[responseCell.id].output = responseCell.output
            notebook_start.cells[responseCell.id].layout = responseCell.layout
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as file:
            contents = file.read()
            return notebook.NotebookResponse(notebook=notebook_start, dependencies=notebook.Dependencies(value=contents))
    except FileNotFoundError:
        logger.error('Requirements file not found')

def get_notebook(id=''):
    if id!='':
        try:
            logger.debug("Getting notebook from db with id %s", id)
            #get notebook from the database
            zt_notebook = get_notebook_db(id)
            return(zt_notebook)
        except Exception as e:
            logger.warning("Error when getting notebook %s from db: %s", id, traceback.format_exc())

    try:
        logger.debug("Notebook id is empty")            
        # If it doesn't exist in the database, load it from the TOML file
        with open('notebook.toml', "r") as project_file:
            toml_data = toml.load(project_file)

        try:
            #get notebook from the database
            zt_notebook = get_notebook_db(toml_data['notebookId'])
            logger.debug("Notebook retrieved from db with id %s", toml_data['notebookId'])
            return(zt_notebook)
        except Exception as e:
            logger.debug("Notebook with id %s does not exist in db", toml_data['notebookId'])
            pass
        # Convert TOML data to a Notebook object
        notebook_data = {
            'notebookId' : toml_data['notebookId'],
            'userId' : '',
            'cells': {
                cell_id: notebook.CodeCell(id=cell_id, **cell_data, output="")
                for cell_id, cell_data in toml_data['cells'].items()
            }
        }
        zt_notebook = notebook.Notebook(**notebook_data)
        new_notebook = zt_notebook.model_dump_json()
        conn = duckdb.connect(notebook_db_path)
        conn.execute("INSERT OR REPLACE INTO notebooks (id, notebook) VALUES (?, ?)", [zt_notebook.notebookId,new_notebook])
        conn.close()
        logger.debug("Notebook with id %s loaded from toml and new db entry created", toml_data['notebookId'])
        return zt_notebook

    except Exception as e:
        logger.error("Error when loading notebook, return empty notebook: %s", traceback.format_exc())
        # Handle any exceptions appropriately and return a valid notebook object
        return notebook.Notebook(cells={},userId='')

def get_notebook_db(id=''):
    conn = duckdb.connect(notebook_db_path)
    if id!="":
        notebook_data = conn.execute('SELECT notebook FROM notebooks WHERE id = ?',[id]).fetchall()
    conn.close()
    return notebook.Notebook(**json.loads(notebook_data[0][0]))


def globalStateUpdate(newCell: notebook.CodeCell=None, position_key:str=None, deletedCell: str=None, saveCell: request.SaveRequest=None, run_request: request.Request=None, run_response: response.Response=None):
    zt_notebook = get_notebook()
    logger.debug("Updating state for notebook %s", zt_notebook.notebookId)
    try:        
        old_state = zt_notebook.model_dump()
        if newCell is not None:
            if position_key:
                new_cell_dict = OrderedDict()
                for k, v in zt_notebook.cells.items():
                    new_cell_dict[k] = v
                    if k==position_key:
                        new_cell_dict[newCell.id] = newCell
                zt_notebook.cells = new_cell_dict
            else:
                zt_notebook.cells[newCell.id] = newCell
                zt_notebook.cells.move_to_end(newCell.id, last=False)
        if deletedCell is not None:
            del zt_notebook.cells[deletedCell]
        if saveCell is not None:
            zt_notebook.cells[saveCell.id].code=saveCell.text
        if run_request is not None:
            for requestCell in run_request.cells:
                zt_notebook.cells[requestCell.id].code = requestCell.code
                zt_notebook.cells[requestCell.id].variable_name = requestCell.variable_name
        if run_response is not None:
            for responseCell in run_response.cells:
                zt_notebook.cells[responseCell.id].components = responseCell.components
                zt_notebook.cells[responseCell.id].output = responseCell.output
                zt_notebook.cells[responseCell.id].layout = responseCell.layout
        
        new_state = zt_notebook.model_dump()
        new_notebook = zt_notebook.model_dump_json()
        conn = duckdb.connect(notebook_db_path)
        conn.execute("INSERT OR REPLACE INTO notebooks (id, notebook) VALUES (?, ?)", [zt_notebook.notebookId,new_notebook])
        conn.close()
        differences = list(diff(old_state, new_state))
        save_toml(zt_notebook)
    except Exception as e:
        logger.error("Error while updating state for notebook %s: %s", zt_notebook.notebookId, traceback.format_exc())

def save_toml(zt_notebook):
    tmp_uuid_file = f'notebook_{uuid.uuid4()}.toml'
    logger.debug("Saving toml for notebook %s", zt_notebook.notebookId)
    try:
        with open(tmp_uuid_file, "w") as project_file:
            # Write notebookId
            project_file.write(f'notebookId = "{zt_notebook.notebookId}"\n\n')

            for cell_id, cell in zt_notebook.cells.items():
                # Write cell_id as a sub-section under cells
                project_file.write(f'[cells.{cell_id}]\n')
                
                # Write cellType and code for this cell
                project_file.write(f'cellType = "{cell.cellType}"\n')
                
                if cell.cellType=='sql' and cell.variable_name:
                    project_file.write(f'variable_name = "{cell.variable_name}"\n')
                
                # Format code as a multi-line string
                escaped_code = cell.code.encode().decode('unicode_escape')
                project_file.write(f'code = """\n{escaped_code}"""\n\n')
        os.replace(tmp_uuid_file, 'notebook.toml')
    except Exception as e:
        logger.error("Error saving notebook %s toml file: %s", zt_notebook.notebookId, traceback.format_exc())
        
    finally:
        try:
            os.remove(tmp_uuid_file)
        except Exception as e:
            logger.warning("Error while deleting temporary toml file for notebook %s: %s", zt_notebook.notebookId, traceback.format_exc())
            pass  # Handle error silently
    logger.debug("Toml saved for notebook %s", zt_notebook.notebookId)


def remove_user_state(user_id):
    try:
        if user_id in user_states:
            # Cancel and remove the associated timer
            timer = user_states[user_id]['timer']
            if timer:
                timer.cancel()
            del user_states[user_id]
            logger.debug("User state removed for user %s", user_id)
    except Exception as e:
        logger.error("Error removing user state for user %s: %s", user_id, traceback.format_exc())

def timer_set(user_id, timeout_seconds):
    logger.debug("Starting timer for user %s", user_id)
    if user_id in user_states:
        existing_timer = user_states[user_id].get('timer')
        if existing_timer:
            existing_timer.cancel()
        
        timer = threading.Timer(timeout_seconds, remove_user_state, args=(user_id,))
        timer.daemon=True
        timer.start()
        
        user_states[user_id]['timer'] = timer
