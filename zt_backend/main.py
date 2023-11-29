from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import OrderedDict
from zt_backend.models.notebook import Notebook, CodeCell
from zt_backend.config import settings
import zt_backend.router as router
import os
import uuid
import subprocess
import logging
import traceback

app = FastAPI()
logger = logging.getLogger("__name__")

current_path = os.path.dirname(os.path.abspath(__file__))

run_mode = settings.run_mode
project_name = settings.project_name
user_name = settings.user_name

route_prefix = ''
if project_name:
    route_prefix = '/'+user_name+'/'+project_name

app.include_router(router.router, prefix=route_prefix)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@app.on_event("startup")
def open_project():
    try:
        if not os.path.exists('notebook.toml'):
            logger.info("No toml file found, creating with empty notebook")
            codeCell = CodeCell(
                id=str(uuid.uuid4()),
                code='',
                components=[],
                variable_name='',
                output='',
                cellType='code'
            )
            zt_notebook = Notebook(userId='', cells=OrderedDict([(codeCell.id, codeCell)]))
            router.save_toml(zt_notebook=zt_notebook)
        if not os.path.exists('requirements.txt'):
            logger.info("No requirements file found, creating with base dependency")
            with open('requirements.txt', 'w') as file:
                file.write('zero-true')
                subprocess.run("lock requirements.txt")
    except Exception as e:
        logger.error("Error creating new files on startup: %s", traceback.format_exc())
        
if run_mode=='app':
    app.mount(route_prefix, StaticFiles(directory=os.path.join(current_path, "dist_app"), html=True), name="assets")
else:
    app.mount(route_prefix, StaticFiles(directory=os.path.join(current_path, "dist_dev"), html=True), name="assets")