from fastapi import APIRouter
from zt_backend.models import request, notebook, response
from zt_backend.runner.execute_code import execute_request
from zt_backend.models.state import component_values, created_components, context_globals
from zt_backend.models.components.layout import ZTLayout
import uuid
import os
import toml
import json

router = APIRouter()

@router.get("/health")
def health():
    return('UP')

@router.post("/api/runcode")
async def runcode(request: request.Request):
    globalStateUpdate(run_request=request)
    response = execute_request(request)
    print(response.cells[0].layout)
    globalStateUpdate(run_request=request,run_response=response)
    return response

@router.post("/api/component_run")
def runcode(request: request.ComponentRequest):
    print(request)

@router.post("/api/create_cell")
def create_cell(cellRequest: request.CreateRequest):
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
     globalStateUpdate(deletedCell=deleteRequest.cellId)

@router.get("/api/notebook")
def get_notebook():
    return get_notebook()

def get_notebook():
    with open('notebook.toml', "r") as project_file:
        notebook_data = toml.load(project_file)

    # Convert the JSON strings back to ZTLayout objects
    for cell_id, cell_data in notebook_data.get('cells', {}).items():
        layout_str = cell_data.get('layout')
        if layout_str:
            layout_dict = json.loads(layout_str)
            cell_data['layout'] = ZTLayout(**layout_dict)

    return notebook.Notebook(**notebook_data)

def globalStateUpdate(newCell: notebook.CodeCell=None, deletedCell: str=None, run_request: request.Request=None, run_response: response.Response=None):
    zt_notebook = get_notebook()
    if newCell is not None:
        zt_notebook.cells[newCell.id] = newCell
    if deletedCell is not None:
        del zt_notebook.cells[deletedCell]
    if run_request is not None:
        for requestCell in run_request.cells:
            zt_notebook.cells[requestCell.id].code = requestCell.code
            zt_notebook.cells[requestCell.id].variable_name = requestCell.variable_name
    if run_response is not None:
        for responseCell in run_response.cells:
            zt_notebook.cells[responseCell.id].components = responseCell.components
            zt_notebook.cells[responseCell.id].output = responseCell.output
            zt_notebook.cells[responseCell.id].layout = responseCell.layout

    for cell_id, cell in zt_notebook.cells.items():
        if cell.layout:
            cell.layout = json.dumps(cell.layout.dict())
    
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