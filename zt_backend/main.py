from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import OrderedDict
from zt_backend.models.notebook import Notebook, CodeCell
from zt_backend.config import settings
import zt_backend.router as router
import toml
import os
import uuid

app = FastAPI()

current_path = os.path.dirname(os.path.abspath(__file__))


run_mode = settings.run_mode
project_name = ''

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
            code='',
            components=[],
            variable_name='',
            output='',
            cellType='code'
        )
        zt_notebook = Notebook(userId='', cells=OrderedDict([(codeCell.id, codeCell)]))
        with open('notebook.toml', "w") as project_file:
            toml.dump(zt_notebook.model_dump(), project_file)

if run_mode=='app':
    app.mount(route_prefix, StaticFiles(directory=os.path.join(current_path, "dist_app"), html=True), name="assets")
else:
    app.mount(route_prefix, StaticFiles(directory=os.path.join(current_path, "dist_dev"), html=True), name="assets")