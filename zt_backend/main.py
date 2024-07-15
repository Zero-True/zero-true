from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from zt_backend.config import settings
from zt_backend.utils.notebook import get_notebook, write_notebook
from copilot.copilot import copilot_app
import zt_backend.router as router
import os
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
app.mount(route_prefix+"/copilot", copilot_app)

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
        if not os.path.exists('notebook.ztnb'):
            logger.info("No notebook file found, creating with empty notebook")
            write_notebook()
        if not os.path.exists('requirements.txt'):
            logger.info("No requirements file found, creating with base dependency")
            with open('requirements.txt', 'w') as file:
                file.write('zero-true')
            try:
                subprocess.run(['lock', 'requirements.txt'])
            except Exception:
                logger.error("Failed to lock requirements: %s", traceback.format_exc())
        get_notebook()
    except Exception as e:
        logger.error("Error creating new files on startup: %s", traceback.format_exc())
        
if run_mode=='app':
    app.mount(route_prefix, StaticFiles(directory=os.path.join(current_path, "dist_app"), html=True), name="assets")
else:
    app.mount(route_prefix, StaticFiles(directory=os.path.join(current_path, "dist_dev"), html=True), name="assets")