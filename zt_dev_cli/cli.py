#!/usr/bin/env python3

import subprocess
import os
import shutil
import typer
from zt_backend.models.generate_schema import generate_schema
from typing_extensions import Annotated
from typing import Optional
from rich import print 

app = typer.Typer()

def print_ascii_logo():
    ascii_logo="""
_____________________ ________  _______________   ____
\____    /\__    ___/ \______ \ \_   _____/\   \ /   /
  /     /   |    |     |    |  \ |    __)_  \   Y   / 
 /     /_   |    |     |    `   \|        \  \     /  
/_______ \  |____|    /_______  /_______  /   \___/   
        \/                    \/        \/            

    """
    print(f"[purple]{ascii_logo}[/purple]")

def generate_ts():
    os.mkdir('zt_schema')
    generate_schema()
    os.chdir('zt_frontend')
    shutil.rmtree('src/types')
    os.system('yarn json2ts -i ../zt_schema -o src/types')
    os.chdir('..')
    shutil.rmtree('zt_schema')

def build_frontend():
    try:
        shutil.rmtree('zt_backend/dist_dev')
        shutil.rmtree('zt_backend/dist_app')
    except Exception as e:
        print(e)
    os.chdir('zt_frontend')
    os.system('yarn install')
    os.system('yarn run build')
    os.chdir('..')
    shutil.copytree('zt_frontend/dist', 'zt_backend/dist_dev')
    os.chdir('zt_frontend')
    os.system('yarn run buildapp')
    os.chdir('..')
    shutil.copytree('zt_frontend/dist', 'zt_backend/dist_app')

@app.command()
def pyd2ts():
    generate_ts()

@app.command()
def run_yarn_build():
    build_frontend()


@app.command()
def run(mode: Annotated[Optional[str], typer.Argument(help="The mode to run zero-true in, can be one of 'notebook' and 'app'")],
        port: Annotated[Optional[str], typer.Argument(help="Port number to bind to.")]=""):
    
    print_ascii_logo()
    port = port if port else 5173
    
    if mode == 'app':
        os.environ['RUN_MODE'] = 'app'
        frontend_cmd = ["yarn", "run", "app", str(port)]
    else:
        os.environ['RUN_MODE'] = 'dev'
        frontend_cmd = ["yarn", "run", "dev", str(port)]
    backend_cmd = ["start", "uvicorn", "zt_backend.main:app", "--reload"]

    backend_process = subprocess.Popen(backend_cmd, shell=True)
    os.chdir("zt_frontend")
    frontend_process = subprocess.Popen(frontend_cmd, shell=True)

    backend_process.wait()
    frontend_process.wait()

if __name__ == "__main__":
    app()
