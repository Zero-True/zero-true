from typing import OrderedDict
from zt_backend.models.state.user_state import UserState
from zt_backend.models.state.notebook_state import NotebookState
from zt_backend.models.api import request, response
from zt_backend.models import notebook
from zt_backend.utils.debounce import debounce
from zt_backend.config import settings
import logging
import duckdb
import uuid
import os
import traceback
import json
import copy
import rtoml

logger = logging.getLogger("__name__")
notebook_state = NotebookState()

def get_notebook(id=''):
    if id!='':
        try:
            logger.debug("Getting notebook from db with id %s", id)
            #get notebook from the database
            notebook_state.zt_notebook = get_notebook_db(id)
            notebook_state_init()
            return
        except Exception as e:
            logger.debug("Error when getting notebook %s from db: %s", id, traceback.format_exc())

    try:
        logger.debug("Notebook id is empty")            
        # If it doesn't exist in the database, load it from the TOML file
        with open('notebook.ztnb', "r") as project_file:
            toml_data = rtoml.loads(project_file.read().replace('\\','\\\\'))

        try:
            #get notebook from the database
            notebook_state.zt_notebook = get_notebook_db(toml_data['notebookId'])
            logger.debug("Notebook retrieved from db with id %s", toml_data['notebookId'])
            notebook_state_init()
            return
        except Exception as e:
            logger.debug("Error loading notebook with id %s from db: %s", toml_data['notebookId'], traceback.format_exc())
            pass
        # Convert TOML data to a Notebook object
        notebook_data = {
            'notebookId' : toml_data['notebookId'],
            'notebookName' : toml_data.get('notebookName', 'Zero True'),
            'userId' : '',
            'cells': {
                cell_id: notebook.CodeCell(id=cell_id, **cell_data, output="")
                for cell_id, cell_data in toml_data['cells'].items()
            }
        }
        notebook_state.zt_notebook = notebook.Notebook(**notebook_data)
        new_notebook = notebook_state.zt_notebook.model_dump_json()
        conn = duckdb.connect(notebook_state.notebook_db_path)
        create_table_query = f"CREATE TABLE IF NOT EXISTS '{notebook_state.zt_notebook.notebookId}' (id STRING PRIMARY KEY, notebook STRING)"
        conn.execute(create_table_query)
        insert_query = f"INSERT OR REPLACE INTO '{notebook_state.zt_notebook.notebookId}' (id, notebook) VALUES (?, ?)"
        conn.execute(insert_query, [notebook_state.zt_notebook.notebookId, new_notebook])
        conn.close()
        logger.debug("Notebook with id %s loaded from toml and new db entry created", toml_data['notebookId'])
        notebook_state_init()
    except Exception as e:
        logger.error("Error when loading notebook, return empty notebook: %s", traceback.format_exc())

def notebook_state_init():
    cells = []
    components={}
    for cell_key, cell in notebook_state.zt_notebook.cells.items():
        cell_request=request.CodeRequest(
            id=cell.id, 
            code=cell.code,
            variable_name=cell.variable_name,
            nonReactive=cell.nonReactive,
            showTable=cell.showTable,
            cellType=cell.cellType
        )
        for comp in cell.components:
            if hasattr(comp, 'value'):
                components[comp.id] = comp.value
        cells.append(cell_request)
    notebook_state.base_cells = cells
    notebook_state.base_components = components
    if settings.run_mode=='app':
        for cell_key, cell in notebook_state.zt_notebook.cells.items():
            if cell.hideCell or cell.hideCode:
                notebook_state.zt_notebook.cells[cell_key].code = ''

def get_notebook_request():
    return notebook_state.zt_notebook

def get_request_base(origin_id, components=None):
    if components is None:
        return request.Request(
                    originId=origin_id,
                    cells=copy.deepcopy(notebook_state.base_cells),
                    components=copy.deepcopy(notebook_state.base_components)
                )
    else:
        return request.Request(
                    originId=origin_id,
                    cells=copy.deepcopy(notebook_state.base_cells),
                    components=components
                )

def get_notebook_db(id=''):
    conn = duckdb.connect(notebook_state.notebook_db_path)
    if id!="":
        get_notebook_query = f"SELECT notebook FROM '{id}' WHERE id = '{id}'"
        notebook_data = conn.execute(get_notebook_query).fetchall()
        conn.close()
    return notebook.Notebook(**json.loads(notebook_data[0][0]))

def globalStateUpdate(newCell: notebook.CodeCell=None, 
                      position_key:str=None, 
                      deletedCell: str=None, 
                      saveCell: request.SaveRequest=None, 
                      hideCell: request.HideCellRequest=None,
                      hideCode: request.HideCodeRequest=None,
                      expandCode: request.ExpandCodeRequest=None,
                      renameCell: request.NameCellRequest=None,
                      cellReactivity: request.CellReactivityRequest=None,
                      showTable: request.ShowTableRequest=None,
                      run_request: request.Request=None, 
                      run_response: response.Response=None, 
                      new_notebook_name: str="",
                      ):
    logger.debug("Updating state for notebook %s", notebook_state.zt_notebook.notebookId)
    try:        
        old_state = notebook_state.zt_notebook.model_dump()
        if newCell is not None:
            if position_key:
                new_cell_dict = OrderedDict()
                for k, v in notebook_state.zt_notebook.cells.items():
                    new_cell_dict[k] = v
                    if k==position_key:
                        new_cell_dict[newCell.id] = newCell
                notebook_state.zt_notebook.cells = new_cell_dict
            else:
                new_cell_dict = OrderedDict({newCell.id: newCell})
                new_cell_dict.update(notebook_state.zt_notebook.cells)
                notebook_state.zt_notebook.cells = new_cell_dict
        if deletedCell is not None:
            del notebook_state.zt_notebook.cells[deletedCell]
        if saveCell is not None:
            notebook_state.zt_notebook.cells[saveCell.id].code=saveCell.text
        if hideCell is not None:
            notebook_state.zt_notebook.cells[hideCell.cellId].hideCell=hideCell.hideCell
        if hideCode is not None:
            notebook_state.zt_notebook.cells[hideCode.cellId].hideCode=hideCode.hideCode
        if expandCode is not None:
            notebook_state.zt_notebook.cells[expandCode.cellId].expandCode=expandCode.expandCode
        if renameCell is not None:
            notebook_state.zt_notebook.cells[renameCell.cellId].cellName=renameCell.cellName
        if cellReactivity is not None:
            notebook_state.zt_notebook.cells[cellReactivity.cellId].nonReactive=cellReactivity.nonReactive
        if showTable is not None:
            notebook_state.zt_notebook.cells[showTable.cellId].showTable=showTable.showTable
        if run_request is not None:
            for requestCell in run_request.cells:
                #zt_notebook.cells[requestCell.id].code = requestCell.code
                notebook_state.zt_notebook.cells[requestCell.id].variable_name = requestCell.variable_name
        if run_response is not None:
            for responseCell in run_response.cells:
                notebook_state.zt_notebook.cells[responseCell.id].components = responseCell.components
                notebook_state.zt_notebook.cells[responseCell.id].output = responseCell.output
                notebook_state.zt_notebook.cells[responseCell.id].layout = responseCell.layout
        if new_notebook_name:
            notebook_state.zt_notebook.notebookName = new_notebook_name
        save_notebook()
    except Exception as e:
        logger.error("Error while updating state for notebook %s: %s", notebook_state.zt_notebook.notebookId, traceback.format_exc())

@debounce(5)
def save_notebook():
    new_notebook = notebook_state.zt_notebook.model_dump_json()
    conn = duckdb.connect(notebook_state.notebook_db_path)
    insert_query = f"INSERT OR REPLACE INTO '{notebook_state.zt_notebook.notebookId}' (id, notebook) VALUES (?, ?)"
    conn.execute(insert_query, [notebook_state.zt_notebook.notebookId, new_notebook])
    conn.close()
    write_notebook()

def write_notebook():
    tmp_uuid_file = f'notebook_{uuid.uuid4()}.ztnb'
    logger.debug("Saving toml for notebook %s", notebook_state.zt_notebook.notebookId)
    try:
        with open(tmp_uuid_file, "w") as project_file:
            # Write notebookId
            project_file.write(f'notebookId = "{notebook_state.zt_notebook.notebookId}"\nnotebookName = "{notebook_state.zt_notebook.notebookName}"\n\n')

            for cell_id, cell in notebook_state.zt_notebook.cells.items():
                project_file.write(f'[cells.{cell_id}]\n')
                project_file.write(f'cellName = "{cell.cellName}"\n')
                project_file.write(f'cellType = "{cell.cellType}"\n')
                project_file.write(f'hideCell = "{cell.hideCell}"\n')
                project_file.write(f'hideCode = "{cell.hideCode}"\n')
                project_file.write(f'expandCode = "{cell.expandCode}"\n')
                project_file.write(f'showTable = "{cell.showTable}"\n')
                project_file.write(f'nonReactive = "{cell.nonReactive}"\n')
                
                if cell.cellType=='sql':
                    if cell.variable_name:
                        project_file.write(f'variable_name = "{cell.variable_name}"\n')
                
                # Format code as a multi-line string
                escaped_code = cell.code.encode().decode('unicode_escape').replace('"""',"'''")
                project_file.write(f'code = """\n{escaped_code}"""\n\n')
        os.replace(tmp_uuid_file, 'notebook.ztnb')
    except Exception as e:
        logger.error("Error saving notebook %s toml file: %s", notebook_state.zt_notebook.notebookId, traceback.format_exc())
        
    finally:
        try:
            os.remove(tmp_uuid_file)
        except Exception as e:
            logger.debug("Error while deleting temporary toml file for notebook %s: %s", notebook_state.zt_notebook.notebookId, traceback.format_exc())
            pass  # Handle error silently
    logger.debug("Toml saved for notebook %s", notebook_state.zt_notebook.notebookId)

async def save_worker(save_queue):
    while True:
        message = await save_queue.get()
        globalStateUpdate(**message)

async def websocket_message_sender(execution_state: UserState):
    while True:
        message = await execution_state.message_queue.get()
        await execution_state.websocket.send_json(message)