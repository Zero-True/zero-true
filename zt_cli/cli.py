#!/usr/bin/env python3

import os
import typer
from typing_extensions import Annotated
import uvicorn
from typing import Optional
from rich import print
from pathlib import Path
import shutil
import requests
import pkg_resources
import sys
import yaml
import json
import uuid
import re

cli_app = typer.Typer()


def print_ascii_logo():
    ascii_logo = """

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
        files = {"file": open(zip_path, "rb")}
        r = requests.post(signed_url["url"], data=signed_url["fields"], files=files)
        if r.status_code == 204:
            typer.echo("Successfully uploaded to S3.")
        else:
            typer.echo(f"Failed to upload to S3: {r.content}")
    except Exception as e:
        typer.echo(f"An error occurred: {e}")


@cli_app.command()
def publish(
    key: Annotated[
        str, typer.Argument(help="The API key used to publish your project")
    ],
    user_name: Annotated[
        str, typer.Argument(help="User Name to publish the project under")
    ],
    project_name: Annotated[str, typer.Argument(help="The project to be published")],
    project_source: Annotated[
        str, typer.Argument(help="The directory for your project")
    ],
    team_name: Annotated[
        str,
        typer.Argument(
            help="Optional team for this to be published to. Must have access to this team."
        ),
    ] = "",
    compute_profile: Annotated[
        str,
        typer.Option(
            help="Options: xsmall, small, medium, large, xlarge. Default is xsmall.",
        ),
    ] = "xsmall",
    private: Annotated[
        bool,
        typer.Option(
            "--private/--public",
            help="Project will be published as private by default. Use --public to make it public.",
        ),
    ] = True,
):

    # Step 1: Verify the API key and get a signed URL from the Lambda function
    headers = {"Content-Type": "application/json", "x-api-key": key}
    user_name = user_name.lower().strip()
    project_name = project_name.lower().strip()
    compute_profile = compute_profile.lower().strip()
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    zt_version = pkg_resources.get_distribution("zero-true").version
    if team_name:
        if compute_profile not in ["xsmall", "small", "medium", "large", "xlarge"]:
            typer.echo("Invalid compute profile")
            return
        team_name = re.sub(r"\s+", "-", team_name.lower().strip())
        s3_key = team_name + "/" + project_name + "/" + project_name + ".tar.gz"
        lambda_url = "https://bxmm0wp9zk.execute-api.us-east-2.amazonaws.com/default/team_project_upload"
        response = requests.post(
            lambda_url,
            json={
                "s3_key": s3_key,
                "user_name": user_name,
                "python_version": python_version,
                "zero_true_version": zt_version,
                "compute_profile": compute_profile,
                "private": private,
            },
            headers=headers,
        )
    else:
        if compute_profile not in ["xsmall", "small", "medium"]:
            typer.echo("Invalid compute profile for individual project")
            return
        s3_key = user_name + "/" + project_name + "/" + project_name + ".tar.gz"
        lambda_url = "https://bxmm0wp9zk.execute-api.us-east-2.amazonaws.com/default/project_upload"
        response = requests.post(
            lambda_url,
            json={
                "s3_key": s3_key,
                "python_version": python_version,
                "zero_true_version": zt_version,
                "compute_profile": compute_profile,
                "private": private,
            },
            headers=headers,
        )

    if response.status_code != 200:
        typer.echo(f"Execution error occured: {response.content}")
        return
    response_json = response.json()
    signed_url = response_json.get("uploadURL")
    if not signed_url:
        typer.echo("Failed to get a signed URL.")
        return
    
    python_warning = response_json.get("pythonWarning", None)
    zt_warning = response_json.get("ztWarning", None)
    project_warning = response_json.get("projectWarning", None)
    if python_warning:
        typer.echo(python_warning)
    if zt_warning:
        typer.echo(zt_warning)
    if project_warning:
        typer.echo(project_warning)
    
    if python_warning or zt_warning or project_warning:
        if typer.confirm("Do you want to continue anyway?"):
            pass
        else:
            return

    # Step 2: Zip the project files using shutil
    output_filename = f"{project_name}"
    if project_source == ".":
        project_source = os.path.basename(os.path.normpath(os.getcwd()))
        os.chdir("..")

    shutil.make_archive(
        base_name=output_filename, format="gztar", root_dir=project_source
    )

    # Step 3: Upload zip to S3 using the signed URL
    upload_to_s3(signed_url, f"{output_filename}.tar.gz")
    os.remove(f"{output_filename}.tar.gz")
    return signed_url


@cli_app.command()
def app(
    host: Annotated[
        Optional[str], typer.Option(help="Host address to bind to.")
    ] = "localhost",
    port: Annotated[Optional[int], typer.Option(help="Port number to bind to.")] = 2613,
    remote: Annotated[
        Optional[bool], typer.Option(help="For running zero-true on remote server. ")
    ] = False,
):
    """
    Start the Zero-True application.
    """
    os.environ["ZT_PATH"] = str(Path.cwd())
    print_ascii_logo()
    os.environ["RUN_MODE"] = "app"
    log_path = os.path.normpath(
        pkg_resources.resource_filename("zt_cli", "log_config.yaml")
    )

    print(f"[yellow]Starting Zero-True in app mode on http://{host}:{port}[/yellow]")

    with open(log_path) as f:
        log_config_dict = yaml.full_load(f)

    if not remote:
        os.environ["WS_URL"] = f"ws://{host}:{port}/"
        os.environ["LOCAL_URL"] = f"http://{host}:{port}/"

    uvicorn.run("zt_backend.main:app", host=host, port=port, ws_max_size=209715200, log_config=log_config_dict)


@cli_app.command()
def notebook(
    host: Annotated[
        Optional[str], typer.Option(help="Host address to bind to.")
    ] = "localhost",
    port: Annotated[Optional[int], typer.Option(help="Port number to bind to.")] = 1326,
    remote: Annotated[
        Optional[bool], typer.Option(help="For running zero-true on remote server.")
    ] = False,
):
    """
    Start the Zero-True application.
    """
    os.environ["ZT_PATH"] = str(Path.cwd())
    print_ascii_logo()
    os.environ["RUN_MODE"] = "dev"
    log_path = os.path.normpath(
        pkg_resources.resource_filename("zt_cli", "log_config.yaml")
    )

    print(
        f"[yellow]Starting Zero-True in notebook mode on http://{host}:{port}[/yellow]"
    )

    with open(log_path) as f:
        log_config_dict = yaml.full_load(f)

    if not remote:
        os.environ["WS_URL"] = f"ws://{host}:{port}/"
        os.environ["LOCAL_URL"] = f"http://{host}:{port}/"

    uvicorn.run("zt_backend.main:app", host=host, port=port, ws_max_size=209715200, log_config=log_config_dict)


@cli_app.command()
def jupyter_convert(
    ipynb_path: Annotated[str, typer.Argument(help="The path to the .ipynb file")],
    ztnb_path: Annotated[
        Optional[str], typer.Argument(help="The path to the output .ztnb file")
    ] = "notebook.ztnb",
):
    """
    Convert a Jupyter notebook to a Zero-True notebook.
    """

    # Add notebook.ztnb if not specified in the output path
    if not ztnb_path.endswith("notebook.ztnb"):
        ztnb_path = os.path.join(ztnb_path, "notebook.ztnb")

    try:
        with open(ipynb_path, "r", encoding="utf-8") as f:
            notebook = json.loads(f.read())
    except Exception as e:
        typer.echo(f"Error occured: {e}")
        return
    else:
        output = []

        output.append(f'notebookId = "{uuid.uuid4()}"')
        output.append('notebookName = "Zero True"')
        output.append("")
        output.extend(
            line for line in create_ztnb_cell('"code"', ["import zero_true as zt"])
        )

        # Create only code or markdown cells
        for cell in notebook["cells"]:
            if cell["cell_type"] in ["code", "markdown"]:
                output.extend(
                    line
                    for line in create_ztnb_cell(
                        f'"{cell["cell_type"]}"', cell["source"]
                    )
                )

        with open(ztnb_path, "w", encoding="utf-8") as f:
            for item in output:
                f.write(item + "\n")

        typer.echo(f"Successfully converted {ipynb_path} to {ztnb_path}")
        return


def create_ztnb_cell(cell_type, source):

    common_attributes = {
        "cellName": '""',
        "cellType": '"code"',
        "hideCell": '"False"',
        "hideCode": '"False"',
        "expandCode": '"False"',
        "showTable": '"False"',
        "nonReactive": '"False"',
        "code": '"""',
    }

    cell_content = []
    cell_content.append(f"[cells.{uuid.uuid4()}]")

    for key, value in common_attributes.items():
        if key == "cellType":
            cell_content.append(f"{key} = {cell_type}")
        else:
            cell_content.append(f"{key} = {value}")

    for line in source:
        if cell_type == '"code"':
            escaped_code = line.encode().decode("unicode_escape").replace('"""', "'''")
            cell_content.append(escaped_code)
        else:
            cell_content.append(line)
    cell_content[-1] = cell_content[-1] + '"""'
    cell_content.append("")

    return cell_content


if __name__ == "__main__":
    cli_app()
