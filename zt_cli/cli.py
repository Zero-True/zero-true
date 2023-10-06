#!/usr/bin/env python3

import argparse
import os
import uvicorn

def start_servers():
    parser = argparse.ArgumentParser(description="Start the frontend and backend servers.")
    parser.add_argument("mode", choices=["notebook", "app"], help="The mode to run the servers in.")  # Updated choices
    args = parser.parse_args()

    if args.mode == 'app':
        os.environ['RUN_MODE'] = 'app'
        uvicorn.run('zt_backend.main:app', port=2613)
    elif args.mode=='notebook':
        os.environ['RUN_MODE'] = 'dev'
        uvicorn.run('zt_backend.main:app', port=1326)
    else:
        raise Exception('You must specify either noteboook or app to run Zero-True')

if __name__ == "__main__":
    start_servers()
