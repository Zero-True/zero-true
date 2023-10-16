#!/usr/bin/env python3

import os
import typer
from typing_extensions import Annotated
import logging
import uvicorn
from typing import Optional

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
    print(ascii_logo)

@app.command()
def start(mode: Annotated[Optional[str], typer.Argument(help="The mode to run zero-true in, can be one of 'notebook' and 'app'")],
          host: Annotated[Optional[str], typer.Argument(help="Host address to bind to.")]="0.0.0.0",
          port: Annotated[Optional[str],typer.Argument(help="Port number to bind to.")]=""):
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
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    if host == "0.0.0.0":
        host = 'localhost'
    logger.info(f'Starting Zero-True in {mode} mode on http://{host}:{port}')

    uvicorn.run('zt_backend.main:app', host=host, port=port, log_level='error')

if __name__ == "__main__":
    app()
