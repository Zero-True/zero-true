from fastapi import APIRouter
from fastapi.responses import FileResponse
from models import Request
from runner.execute_code import execute_request
import os

router = APIRouter()

@router.get("/")
def read_root():
    if os.environ.get('RUN_MODE', 'app')=='app':
        return FileResponse("dist_app/index.html")
    return FileResponse("dist_dev/index.html")

@router.get("/health")
def health():
    return('UP')

@router.post("/api/runcode")
def runcode(request: Request):
    return execute_request(request)