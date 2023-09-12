from fastapi import APIRouter, Request
from fastapi.responses import FileResponse
from zt_backend.models import request
from zt_backend.models import notebook
from runner.execute_code import execute_request
import os
import uuid

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
async def runcode(request: request.Request):
    return execute_request(request)

@router.post("/api/create_cell")
def create_cell():
     return notebook.CodeCell(
         id=str(uuid.uuid4()),
         code='#code here or else',
         components=[],
         output='',
         cellType='code'
     )