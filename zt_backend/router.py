from fastapi import APIRouter,BackgroundTasks
from zt_backend.models import request, notebook, response
from zt_backend.runner.execute_code import execute_request
from zt_backend.config import settings
from dictdiffer import diff
import re
import site 
import json
import duckdb
import uuid
import os
import toml
import threading



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

@router.get("/health")
def health():
    return('UP')

@router.post("/api/runcode")
async def runcode(request: request.Request,background_tasks: BackgroundTasks):
    if(run_mode=='dev'):
        background_tasks.add_task(globalStateUpdate,run_request=request.model_copy(deep=True))

        response = execute_request(request, cell_outputs_dict)
        background_tasks.add_task(globalStateUpdate,run_response=response)
        return response

@router.post("/api/component_run")
def runcode(component_request: request.ComponentRequest):
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
            return response.Response(cells=[], refresh=True)
        timer_set(component_request.userId, 1800)
        return execute_request(code_request, user_states[component_request.userId])



@router.post("/api/create_cell")
def create_cell(cellRequest: request.CreateRequest):
     if(run_mode=='dev'):
        createdCell = notebook.CodeCell(
            id=str(uuid.uuid4()),
            code='',
            components=[],
            output='',
            variable_name='',
            cellType=cellRequest.cellType
        )
        globalStateUpdate(newCell=createdCell.model_copy(deep=True))
        return createdCell

@router.post("/api/delete_cell")
def delete_cell(deleteRequest: request.DeleteRequest):
     cell_id = deleteRequest.cellId
     if(run_mode=='dev'):
        
        try:
            del cell_outputs_dict[cell_id]
        except Exception as e:
            print(e)
        try:
            
            cell_dict = cell_outputs_dict['previous_dependecy_graph'].cells
            if cell_id in cell_dict:
                del cell_dict[cell_id]

            # Recursively search for and remove the cell ID from child_cells in other cells
            for cell_key, cell in cell_dict.items():
                if cell_id in dict(cell).get("child_cells", []):
                    cell["child_cells"].remove(cell_id)

            # Recursively search for and remove the cell ID from parent_cells in other cells
            for cell_key, cell in cell_dict.items():
                if cell_id in dict(cell).get("parent_cells", []):
                    cell["parent_cells"].remove(cell_id)

        except Exception as e:
            print(e)

        globalStateUpdate(deletedCell=deleteRequest.cellId)

@router.post("/api/save_text")
def save_text(saveRequest: request.SaveRequest):
     if(run_mode=='dev'):
        globalStateUpdate(saveCell=saveRequest)

@router.post("/api/clear_state")
def clear_state(clearRequest: request.ClearRequest):
     if(run_mode=='app'):
        user_states.pop(clearRequest.userId, None)

@router.get("/api/notebook")
def get_notebook():
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
    return notebook_start

def get_notebook(id=''):
    if id!='':
        try:
            #get notebook from the database
            zt_notebook = get_notebook_db(id)
            return(zt_notebook)
        except Exception as e:
            print(e)

    try:            
        # If it doesn't exist in the database, load it from the TOML file
        with open('notebook.toml', "r") as project_file:
            toml_data = toml.load(project_file)

        try:
        #get notebook from the database
            zt_notebook = get_notebook_db(toml_data['notebookId'])
            return(zt_notebook)
        except Exception as e:
            pass
        # Convert TOML data to a Notebook object
        notebook_data = {
            'notebookId' : toml_data['notebookId'],
            'userId' : '',
            'cells': {
                cell_id: notebook.CodeCell(id=cell_id, **cell_data,output="",variable_name='')
                for cell_id, cell_data in toml_data['cells'].items()
            }
        }
        zt_notebook = notebook.Notebook(**notebook_data)
        new_notebook = zt_notebook.model_dump_json()
        conn = duckdb.connect(notebook_db_path)
        conn.execute("INSERT OR REPLACE INTO notebooks (id, notebook) VALUES (?, ?)", [zt_notebook.notebookId,new_notebook])
        conn.close()
        return zt_notebook

    except Exception as e:
        print(e)
        # Handle any exceptions appropriately and return a valid notebook object
        return notebook.Notebook(cells={},userId='')


def get_notebook_db(id=''):
    conn = duckdb.connect(notebook_db_path)
    if id!="":
        notebook_data = conn.execute('SELECT notebook FROM notebooks WHERE id = ?',[id]).fetchall()
    conn.close()
    return notebook.Notebook(**json.loads(notebook_data[0][0]))


def globalStateUpdate(newCell: notebook.CodeCell=None, deletedCell: str=None, saveCell: request.SaveRequest=None, run_request: request.Request=None, run_response: response.Response=None):
    
    zt_notebook = get_notebook()
    
    
    old_state = zt_notebook.model_dump()
    if newCell is not None:
        zt_notebook.cells[newCell.id] = newCell
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


    #print("Differences:", differences)

def save_toml(zt_notebook):
    tmp_uuid_file = f'notebook_{uuid.uuid4()}.toml'

    try:
        with open(tmp_uuid_file, "w") as project_file:
            # Write notebookId
            project_file.write(f'notebookId = "{zt_notebook.notebookId}"\n\n')

            for cell_id, cell in zt_notebook.cells.items():
                # Write cell_id as a sub-section under cells
                project_file.write(f'[cells.{cell_id}]\n')
                
                # Write cellType and code for this cell
                project_file.write(f'cellType = "{cell.cellType}"\n')
                
                # Format code as a multi-line string
                escaped_code = cell.code.encode().decode('unicode_escape')
                project_file.write(f'code = """\n{escaped_code}"""\n\n')

        os.replace(tmp_uuid_file, 'notebook.toml')

    except Exception as e:
        print(e)
        
    finally:
        try:
            os.remove(tmp_uuid_file)
        except Exception as e:
            pass  # Handle error silently



def remove_user_state(user_id):
    if user_id in user_states:
        # Cancel and remove the associated timer
        timer = user_states[user_id]['timer']
        if timer:
            timer.cancel()
        del user_states[user_id]

def timer_set(user_id, timeout_seconds):
    if user_id in user_states:
        existing_timer = user_states[user_id].get('timer')
        if existing_timer:
            existing_timer.cancel()
        
        timer = threading.Timer(timeout_seconds, remove_user_state, args=(user_id,))
        timer.start()
        
        user_states[user_id]['timer'] = timer
