#!/usr/bin/env python3

import subprocess
import os
import shutil
import typer
from zt_backend.models.generate_schema import generate_schema
from typing_extensions import Annotated
from typing import Optional
from rich import print 
import requests

app = typer.Typer()

def upload_to_s3(signed_url, zip_path):
    try:
        files = { 'file': open(zip_path, 'rb')}
        r = requests.post(signed_url['url'],data=signed_url['fields'],files=files)
        if r.status_code == 204:
            typer.echo("Successfully uploaded to S3.")
        else:
            typer.echo(f"Failed to upload to S3: {r.content}")
    except Exception as e:
        typer.echo(f"An error occurred: {e}")


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
def publish(key: Annotated[Optional[str],typer.Argument(help="The API key used to publish your project")],
            user_name: Annotated[Optional[str],typer.Argument(help="User Name to publish the project under")],
            project_name:  Annotated[Optional[str],typer.Argument(help="The project to be published")],
            project_source: Annotated[Optional[str],typer.Argument(help="The directory for your project")]):
    
    s3_key = user_name+'/'+ project_name+'/'+project_name+'.zip'
    # Step 1: Verify the API key and get a signed URL from the Lambda function
    lambda_url = "https://1z4pa3de8d.execute-api.us-east-1.amazonaws.com/default/project_upload"
    headers = {"Content-Type":"application/json",
               "x-api-key":key}
    response = requests.post(lambda_url, json={"s3_key": s3_key},headers=headers)
    
    if response.status_code != 200:
        typer.echo(f"API key verification failed: {response.content}")
        return
    signed_url = response.json().get("uploadURL")
    if not signed_url:
        typer.echo("Failed to get a signed URL.")
        return

    # Step 2: Zip the project files using shutil
    output_filename = f"{project_name}"
    if project_source == '.':
        project_source = os.path.basename(os.path.normpath(os.getcwd()))
        print(project_source)
        os.chdir('..')

    shutil.make_archive(base_name =output_filename,format='zip', root_dir = project_source)

    # Step 3: Upload zip to S3 using the signed URL
    
    upload_to_s3(signed_url, f"{output_filename}.zip")
    os.remove(f"{output_filename}.zip")
    return signed_url


    

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
