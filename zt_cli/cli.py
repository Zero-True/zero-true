#!/usr/bin/env python3

import argparse
import subprocess
import os
import zt_backend.models as models

def start_servers():
    parser = argparse.ArgumentParser(description="Start the frontend and backend servers.")
    parser.add_argument("mode", choices=["dev", "app"], help="The mode to run the servers in.")  # Updated choices
    args = parser.parse_args()

    if args.mode == 'app':
        os.environ['RUN_MODE'] = 'app'
    else:
        os.environ['RUN_MODE'] = 'dev'

    os.chdir("zt_backend")
    backend_process = subprocess.Popen(["uvicorn", "main:app"])
    
    backend_process.wait()    

if __name__ == "__main__":
    start_servers()
