from fastapi import APIRouter
from fastapi.responses import FileResponse
from zt_backend.models import request
from runner.execute_code import execute_request
import os

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
    here= execute_request(request)
    print(here.model_dump())
    return here.model_dump()