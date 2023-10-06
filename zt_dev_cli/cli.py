#!/usr/bin/env python3

import argparse
import subprocess
import os
import shutil
from zt_backend.models.generate_schema import generate_schema

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

def start_servers(args):
    if args.mode == 'app':
        os.environ['RUN_MODE'] = 'app'
        frontend_cmd = ["yarn", "run", "app", str(args.frontend_port)]
    else:
        os.environ['RUN_MODE'] = 'dev'
        frontend_cmd = ["yarn", "run", "dev", str(args.frontend_port)]
    backend_cmd = ["start", "uvicorn", "zt_backend.main:app", "--reload"]

    backend_process = subprocess.Popen(backend_cmd, shell=True)
    os.chdir("zt_frontend")
    frontend_process = subprocess.Popen(frontend_cmd, shell=True)

    backend_process.wait()
    frontend_process.wait()

def zt_cli():
    parser = argparse.ArgumentParser(description="Start the frontend and backend servers.")
    parser.add_argument("run", nargs='?', default=False, help="Run the project")
    parser.add_argument("mode", choices=["notebook", "app"], nargs='?', default="app", help="The mode to run the servers in.")
    parser.add_argument("--frontend-port", type=int, default=5173, help="The port for the frontend server.") # Default to 8080
    parser.add_argument("--pyd2ts", action=argparse.BooleanOptionalAction, help="Generate TS models without running project")
    parser.add_argument("--yarnBuild", action=argparse.BooleanOptionalAction, help="Generate TS models without running project")
    args = parser.parse_args()

    if args.pyd2ts:
        generate_ts()
    if args.yarnBuild:
        build_frontend()
    if args.run:
        start_servers(args)
    
if __name__ == "__main__":
    zt_cli()
