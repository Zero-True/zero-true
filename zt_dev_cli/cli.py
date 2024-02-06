#!/usr/bin/env python3

import subprocess
import os
import shutil
import typer
from zt_backend.models.generate_schema import generate_schema
from typing_extensions import Annotated
from typing import Optional
from rich import print
import pkg_resources

cli_app = typer.Typer()

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
        typer.echo(e)
    os.chdir('zt_frontend')
    os.system('yarn install')
    os.system('yarn run build')
    os.chdir('..')
    shutil.copytree('zt_frontend/dist', 'zt_backend/dist_dev')
    os.chdir('zt_frontend')
    os.system('yarn run buildapp')
    os.chdir('..')
    shutil.copytree('zt_frontend/dist', 'zt_backend/dist_app')

@cli_app.command()
def pyd2ts():
    generate_ts()

@cli_app.command()
def build():
    build_frontend()    

@cli_app.command()
def app(port: Annotated[Optional[int], typer.Argument(help="Port number to bind to.")]=5173):
    
    print_ascii_logo()

    log_path = os.path.normpath(pkg_resources.resource_filename('zt_dev_cli', 'log_config.yaml'))
    os.environ['RUN_MODE'] = 'app'
    frontend_cmd = ["yarn", "run", "app", str(port)]
    backend_cmd = ["uvicorn", "zt_backend.main:app", "--reload", f"--log-config={log_path}"]
    if (os.name == 'nt'):
        backend_cmd = ["start"]+backend_cmd

    backend_process = subprocess.Popen(backend_cmd, shell=(os.name == 'nt'))
    os.chdir("zt_frontend")
    frontend_process = subprocess.Popen(frontend_cmd, shell=(os.name == 'nt'))

    backend_process.wait()
    frontend_process.wait()

@cli_app.command()
def notebook(port: Annotated[Optional[int], typer.Argument(help="Port number to bind to.")]=5173):
    
    print_ascii_logo()

    log_path = os.path.normpath(pkg_resources.resource_filename('zt_dev_cli', 'log_config.yaml'))
    os.environ['RUN_MODE'] = 'dev'
    frontend_cmd = ["yarn", "run", "dev", str(port)]
    backend_cmd = ["uvicorn", "zt_backend.main:app", "--reload", f"--log-config={log_path}"]
    if (os.name == 'nt'):
        backend_cmd = ["start"]+backend_cmd

    backend_process = subprocess.Popen(backend_cmd, shell=(os.name == 'nt'))
    os.chdir("zt_frontend")
    frontend_process = subprocess.Popen(frontend_cmd, shell=(os.name == 'nt'))

    backend_process.wait()
    frontend_process.wait()

if __name__ == "__main__":
    cli_app()