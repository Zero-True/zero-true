#!/usr/bin/env python3

import os
import typer
from typing_extensions import Annotated
import uvicorn
from typing import Optional
from rich import print
import shutil
import requests
import pkg_resources
import yaml

cli_app = typer.Typer()

def print_ascii_logo():
    ascii_logo="""

_______________________________ ________    _____________________ ____ ______________
\____    /\_   _____/\______   \\_____  \   \__    ___/\______   \    |   \_   _____/
  /     /  |    __)_  |       _/ /   |   \    |    |    |       _/    |   /|    __)_ 
 /     /_  |        \ |    |   \/    |    \   |    |    |    |   \    |  / |         |
/_______ \/_______  / |____|_  /\_______  /   |____|    |____|_  /______/ /_______  /
        \/        \/         \/         \/                     \/                 \/ 

    """
    print(f"[purple]{ascii_logo}[/purple]")

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

@cli_app.command()
def publish(key: Annotated[Optional[str],typer.Argument(help="The API key used to publish your project")],
            user_name: Annotated[Optional[str],typer.Argument(help="User Name to publish the project under")],
            project_name:  Annotated[Optional[str],typer.Argument(help="The project to be published")],
            project_source: Annotated[Optional[str],typer.Argument(help="The directory for your project")]):
    
    s3_key = user_name+'/'+ project_name+'/'+project_name+'.zip'
    # Step 1: Verify the API key and get a signed URL from the Lambda function
    lambda_url = "https://mxj5v1635d.execute-api.us-east-1.amazonaws.com/default/project_upload"
    headers = {"Content-Type":"application/json",
               "x-api-key":key}
    response = requests.post(lambda_url, json={"s3_key": s3_key}, headers=headers)

    if response.status_code != 200:
        typer.echo(f"Execution error occured: {response.content}")
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

@cli_app.command()
def app(host: Annotated[Optional[str], typer.Argument(help="Host address to bind to.")]="localhost",
        port: Annotated[Optional[int], typer.Argument(help="Port number to bind to.")]=2613):
    """
    Start the Zero-True application.
    """

    print_ascii_logo()
    os.environ['RUN_MODE'] = 'app'
    log_path = os.path.normpath(pkg_resources.resource_filename('zt_cli', 'log_config.yaml'))
        
    print(f"[yellow]Starting Zero-True in app mode on http://{host}:{port}[/yellow]")

    with open(log_path) as f:
        log_config_dict = yaml.full_load(f)
    
    uvicorn.run('zt_backend.main:app', host=host, port=port, log_config=log_config_dict)

@cli_app.command()
def notebook(host: Annotated[Optional[str], typer.Argument(help="Host address to bind to.")]="localhost",
        port: Annotated[Optional[int], typer.Argument(help="Port number to bind to.")]=1326):
    """
    Start the Zero-True application.
    """

    print_ascii_logo()
    os.environ['RUN_MODE'] = 'dev'
    log_path = os.path.normpath(pkg_resources.resource_filename('zt_cli', 'log_config.yaml'))
        
    print(f"[yellow]Starting Zero-True in notebook mode on http://{host}:{port}[/yellow]")

    with open(log_path) as f:
        log_config_dict = yaml.full_load(f)
    
    uvicorn.run('zt_backend.main:app', host=host, port=port, log_config=log_config_dict)

if __name__ == "__main__":
    cli_app()