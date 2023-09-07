#!/usr/bin/env python3

import argparse
import subprocess
import os

def start_servers():
    parser = argparse.ArgumentParser(description="Start the frontend and backend servers.")
    parser.add_argument("mode", choices=["dev", "app"], help="The mode to run the servers in.")  # Updated choices
    parser.add_argument("--developer", action=argparse.BooleanOptionalAction, help="Run in developer mode with hot reloading")
    parser.add_argument("--frontend-port", type=int, default=5173, help="The port for the frontend server.") # Default to 8080
    args = parser.parse_args()

    if args.mode == 'app':
        os.environ['RUN_MODE'] = 'app'
        frontend_cmd = ["yarn", "run", "app", str(args.frontend_port)] # Pass port as argument here
    else:
        os.environ['RUN_MODE'] = 'dev'
        frontend_cmd = ["yarn", "run", "dev", str(args.frontend_port)] # Pass port as argument here
    backend_cmd = ["uvicorn", "main:app", "--reload"]

    os.chdir("zt_backend")
    backend_process = subprocess.Popen(backend_cmd)

    if args.developer:
        os.chdir("../zt_frontend")
        frontend_process = subprocess.Popen(frontend_cmd, shell=True)
        frontend_process.wait()
    
    backend_process.wait()

if __name__ == "__main__":
    start_servers()
