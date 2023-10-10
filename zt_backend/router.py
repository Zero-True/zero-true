from fastapi import APIRouter,BackgroundTasks
from zt_backend.models import request, notebook, response
from zt_backend.runner.execute_code import execute_request
from zt_backend.config import settings
import tomli
import uuid
import os
import toml
import json

router = APIRouter()

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
    components={}
    for cell_key, cell in notebook.cells.items():
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
    components[component_request.componentId] = component_request.componentValue
    code_request = request.Request(
        originId=component_request.originId,
        cells=cells,
        components=components
    )
    if(run_mode=='dev'):
        return execute_request(code_request, cell_outputs_dict)
    else:
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
     if(run_mode=='dev'):
        globalStateUpdate(deletedCell=deleteRequest.cellId)

@router.post("/api/save_text")
def save_test(saveRequest: request.SaveRequest):
     if(run_mode=='dev'):
        globalStateUpdate(saveCell=saveRequest)

@router.get("/api/notebook")
def get_notebook():
    notebook_start = get_notebook()
    if (run_mode=='app'):
        userId = str(uuid.uuid4())
        notebook_start.userId = userId
        user_states[userId]={}
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

def get_notebook():
    with open('notebook.toml', "rb") as project_file:
        notebook_data = tomli.load(project_file)
    return notebook.Notebook(**notebook_data)

def globalStateUpdate(newCell: notebook.CodeCell=None, deletedCell: str=None, saveCell: request.SaveRequest=None, run_request: request.Request=None, run_response: response.Response=None):
    zt_notebook = get_notebook()
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
    
    tmp_uuid_file = 'notebook_'+ str(uuid.uuid4())+'.toml'
    
    try:
        with open(tmp_uuid_file, "w") as project_file:
            toml.dump(zt_notebook.model_dump(), project_file)
        os.replace(tmp_uuid_file,'notebook.toml')

    except Exception as e:
        print(e)
            
    try:
        os.remove(tmp_uuid_file)
    except Exception as e:
        e