from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import OrderedDict
from zt_backend.models.notebook import Notebook, CodeCell
import router
import toml
import os
import uuid

app = FastAPI()

run_mode = os.environ.get('RUN_MODE', 'app')
project_name = os.environ.get('PROJECT_NAME','')

route_prefix = ''
if project_name:
    route_prefix = '/'+project_name+'/'+run_mode

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
    if not os.path.exists('notebook.toml'):
        codeCell = CodeCell(
            id=str(uuid.uuid4()),
            code='#code here or else',
            components=[],
            output='',
            cellType='code'
        )
        zt_notebook = Notebook(cells=OrderedDict([(codeCell.id, codeCell)]))
        with open('notebook.toml', "w") as project_file:
            toml.dump(zt_notebook.model_dump(), project_file)

if run_mode=='app':
    app.mount(route_prefix, StaticFiles(directory="dist_app"), name="assets")
else:
    app.mount(route_prefix, StaticFiles(directory="dist_dev"), name="assets")
