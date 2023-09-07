from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import router
import os

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

if run_mode=='app':
    app.mount(route_prefix, StaticFiles(directory="dist_app"), name="assets")
else:
    app.mount(route_prefix, StaticFiles(directory="dist_dev"), name="assets")
