#!/usr/bin/env python3

import os
import typer
from typing_extensions import Annotated
import uvicorn
from typing import Optional
from rich import print
import shutil
import requests

app = typer.Typer()

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

@app.command()
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

@app.callback(invoke_without_command=True)
def start(mode: Annotated[Optional[str], typer.Argument(help="The mode to run zero-true in, can be one of 'notebook' and 'app'")],
          host: Annotated[Optional[str], typer.Argument(help="Host address to bind to.")]="localhost",
          port: Annotated[Optional[str], typer.Argument(help="Port number to bind to.")]=""):
    """
    Start the Zero-True application.
    """

    print_ascii_logo()
    if mode == 'app':
        os.environ['RUN_MODE'] = 'app'
        port = port if port else 2613
    elif mode == 'notebook':
        os.environ['RUN_MODE'] = 'dev'
        port = port if port else 1326
    else:
        typer.echo("Invalid mode. Choose either 'notebook' or 'app'.")
        raise typer.Exit(code=1)
        
    print(f"[yellow]Starting Zero-True in {mode} mode on http://{host}:{port}[/yellow]")

    uvicorn.run('zt_backend.main:app', host=host, port=port, log_level='info')

if __name__ == "__main__":
    app()