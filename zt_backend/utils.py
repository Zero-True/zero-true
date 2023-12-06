from typing import OrderedDict
from zt_backend.models import request, notebook, response
from dictdiffer import diff
import logging
import duckdb
import uuid
import os
import jedi
import traceback
import site
import json
import rtoml

logger = logging.getLogger("__name__")
notebook_db_dir =  site.USER_SITE+'/.zero_true/'
notebook_db_path = notebook_db_dir+'notebook.db'

def get_notebook(id=''):
    if id!='':
        try:
            logger.debug("Getting notebook from db with id %s", id)
            #get notebook from the database
            zt_notebook = get_notebook_db(id)
            return(zt_notebook)
        except Exception as e:
            logger.debug("Error when getting notebook %s from db: %s", id, traceback.format_exc())

    try:
        logger.debug("Notebook id is empty")            
        # If it doesn't exist in the database, load it from the TOML file
        with open('notebook.toml', "r") as project_file:
            toml_data = rtoml.load(project_file)

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
                new_cell_dict = OrderedDict({newCell.id: newCell})
                new_cell_dict.update(zt_notebook.cells)
                zt_notebook.cells = new_cell_dict
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
                escaped_code = cell.code.encode().decode('unicode_escape').replace('"""',"'''")
                project_file.write(f'code = """\n{escaped_code}"""\n\n')
        os.replace(tmp_uuid_file, 'notebook.toml')
    except Exception as e:
        logger.error("Error saving notebook %s toml file: %s", zt_notebook.notebookId, traceback.format_exc())
        
    finally:
        try:
            os.remove(tmp_uuid_file)
        except Exception as e:
            logger.debug("Error while deleting temporary toml file for notebook %s: %s", zt_notebook.notebookId, traceback.format_exc())
            pass  # Handle error silently
    logger.debug("Toml saved for notebook %s", zt_notebook.notebookId)

def get_code_completions(cell_id:str, code: str, line: int, column: int) -> list:
    script = jedi.Script(code)
    completions = script.complete(line, column)
    return {"cell_id": cell_id, "completions": [{"label": completion.name, "type": completion.type} for completion in completions]}