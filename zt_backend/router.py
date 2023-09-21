from fastapi import APIRouter
from zt_backend.models import request, notebook, response
from zt_backend.runner.execute_code import execute_request
from zt_backend.models.state import component_values, created_components, context_globals
import uuid
import toml

router = APIRouter()

@router.get("/health")
def health():
    return('UP')

@router.post("/api/runcode")
def runcode(request: request.Request):
    response = execute_request(request)
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
         cellType=cellRequest.cellType
     )
     globalStateUpdate(newCell=createdCell)
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
    if run_response is not None:
        for responseCell in run_response.cells:
            zt_notebook.cells[responseCell.id].components = responseCell.components
            zt_notebook.cells[responseCell.id].output = responseCell.output
    with open('notebook.toml', "w") as project_file:
        toml.dump(zt_notebook.model_dump(), project_file)
