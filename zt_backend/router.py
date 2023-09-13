from fastapi import APIRouter
from fastapi.responses import FileResponse
from zt_backend.models import request, notebook, response
from runner.execute_code import execute_request
import os
import uuid
import toml

router = APIRouter()

@router.get("/")
def read_root():
    if os.environ.get('RUN_MODE', 'app')=='app':
        return FileResponse("dist_app/index.html")
    else:
        return FileResponse("dist_dev/index.html")

@router.get("/health")
def health():
    return('UP')

@router.post("/api/runcode")
def runcode(request: request.Request):
    globalStateUpdate(run_request=request)
    response = execute_request(request)
    globalStateUpdate(run_response=response)
    return response

@router.post("/api/create_cell")
def create_cell():
     createdCell = notebook.CodeCell(
         id=str(uuid.uuid4()),
         code='#code here or else',
         components=[],
         output='',
         cellType='code'
     )
     globalStateUpdate(newCell=createdCell)
     return createdCell

@router.get("/api/notebook")
def get_notebook():
    return get_notebook()

def get_notebook():
    with open('notebook.toml', "r") as project_file:
        notebook_data = toml.load(project_file)
    return notebook.Notebook(**notebook_data)

def globalStateUpdate(newCell: notebook.CodeCell=None, run_request: request.Request=None, run_response: response.Response=None):
    zt_notebook = get_notebook()
    if newCell is not None:
        zt_notebook.cells[newCell.id] = newCell
    if run_request is not None:
        for requestCell in run_request.cells:
            zt_notebook.cells[requestCell.id].code = requestCell.code
    if run_response is not None:
        for responseCell in run_response.cells:
            zt_notebook.cells[responseCell.id].components = responseCell.components
            zt_notebook.cells[responseCell.id].output = responseCell.output
    with open('notebook.toml', "w") as project_file:
        toml.dump(zt_notebook.model_dump(), project_file)
