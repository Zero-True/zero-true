#!/usr/bin/env python3

import argparse
import subprocess
import os
import zt_backend
from zt_backend.main import run_app

def start_servers():
    parser = argparse.ArgumentParser(description="Start the frontend and backend servers.")
    parser.add_argument("mode", choices=["dev", "app"], help="The mode to run the servers in.")  # Updated choices
    args = parser.parse_args()

    if args.mode == 'app':
        os.environ['RUN_MODE'] = 'app'
    else:
        os.environ['RUN_MODE'] = 'dev'

    #run_app()

    os.chdir(os.path.dirname(zt_backend.__file__))
    backend_process = subprocess.Popen(["uvicorn", "main:app", "--port=2613"])
    
    backend_process.wait()    

if __name__ == "__main__":
    start_servers()
