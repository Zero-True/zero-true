from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from copilot.copilot_models import BlankRequest, DidOpenTextDocumentParams,\
                           SignInConfirmRequest, GetCompletionsParams\
                            ,DidChangeTextDocumentParams, CopilotPayloadSignInInitiate\
                            ,CopilotPayloadSignInConfirm, CopilotGetCompletionsResult\
                            ,CopilotPayloadSignOut, TextDocumentItem, AcceptRequest, RejectRequest
from zt_backend.utils.debounce import async_debounce
import requests
from typing import Union
import os
from pathlib import Path
import asyncio
import traceback

copilot_app = FastAPI()

copilot_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

copilot_enabled = False
copilot_doc_open = False
version = 0

def is_docker():
    cgroup = Path('/proc/self/cgroup')
    return Path('/.dockerenv').is_file() or cgroup.is_file() and 'docker' in cgroup.read_text()
if is_docker():
    NODE_SERVER_URL = "http://0.0.0.0:3000"
else:
    NODE_SERVER_URL = "http://localhost:3000"

NODE_SERVER_SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))+"/client.js"
NODE_SERVER_NAME = "node-server"

async def start_node_server():
    if not os.path.isfile(NODE_SERVER_SCRIPT_PATH):
        raise Exception(f"Node.js script not found at {NODE_SERVER_SCRIPT_PATH}")

    try:
        proc = await asyncio.create_subprocess_shell(
            "node "+NODE_SERVER_SCRIPT_PATH,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL)
        print("Node server started")
    except Exception as e:
        print(f"An error occurred while starting server: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@copilot_app.post("/start_node_server")
async def start_node_server_route():
    try:
        await start_node_server()
        return {"message": 'Node server started successfully'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@copilot_app.post("/check_status",response_model=Union[CopilotPayloadSignInConfirm,CopilotPayloadSignOut])
async def check_status(req: BlankRequest):
    global copilot_enabled
    try:
        response = requests.post(f"{NODE_SERVER_URL}/sendRequest", json={"method": "checkStatus", "params": {}})
        response.raise_for_status()
        status = response.json().get('status', '')
        if status == "OK" or status == "AlreadySignedIn":
            copilot_enabled = True
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

@copilot_app.post("/sign_in_initiate", response_model=Union[CopilotPayloadSignInInitiate, CopilotPayloadSignInConfirm])
async def sign_in_initiate(req: BlankRequest):
    global copilot_enabled
    try:
        response = requests.post(f"{NODE_SERVER_URL}/sendRequest", json={"method": "signInInitiate", "params": req.dict()})
        response.raise_for_status()
        status = response.json().get('status', '')
        if status == "OK" or status == "AlreadySignedIn":
            copilot_enabled = True
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

@copilot_app.post("/sign_in_confirm",response_model=CopilotPayloadSignInConfirm)
async def sign_in_confirm(req: SignInConfirmRequest):
    global copilot_enabled
    try:
        response = requests.post(f"{NODE_SERVER_URL}/sendRequest", json={"method": "signInConfirm", "params": req.dict()})
        response.raise_for_status()
        status = response.json().get('status', '')
        if status == "OK" or status == "AlreadySignedIn":
            copilot_enabled = True
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

@copilot_app.post("/sign_out",response_model = CopilotPayloadSignOut)
async def sign_in_confirm(req: BlankRequest):
    global copilot_enabled
    try:
        response = requests.post(f"{NODE_SERVER_URL}/sendRequest", json={"method": "signOut", "params": req.dict()})
        response.raise_for_status()
        copilot_enabled = False
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))
    
async def text_document_did_open(params: DidOpenTextDocumentParams):
    global copilot_enabled
    if copilot_enabled:
        try:
            response = requests.post(f"{NODE_SERVER_URL}/sendNotification", json={"method": "textDocument/didOpen", "params": params.dict()})
            response.raise_for_status()
            return {"message": "Notification sent successfully"}
        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail=str(e))

@async_debounce(0.2)
async def text_document_did_change(params):
    global copilot_enabled
    global copilot_doc_open
    global version
    if copilot_enabled:
        try:
            params = DidChangeTextDocumentParams(**params)
            if not copilot_doc_open:
                open_document = TextDocumentItem(uri=params.textDocument.uri, languageId="python", version=version, text=params.contentChanges[0].text)
                open_request = DidOpenTextDocumentParams(textDocument=open_document)
                response = await text_document_did_open(open_request)
                copilot_doc_open = True
                return response
            else:
                version+=1
                params.textDocument.version = version
                response = requests.post(f"{NODE_SERVER_URL}/sendNotification", json={"method": "textDocument/didChange", "params": params.dict()})
                response.raise_for_status()
                return {"message": "ChangeEvent sent successfully"}
        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail=str(e))

@copilot_app.post("/get_completions", response_model=CopilotGetCompletionsResult)
async def get_completions(params: GetCompletionsParams):
    global copilot_enabled
    global copilot_doc_open
    global version
    if copilot_enabled and copilot_doc_open:
        try:
            params.doc.version = version
            response = requests.post(f"{NODE_SERVER_URL}/sendRequest", json={"method": "getCompletions", "params": params.dict()})
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail=str(e))
        
@copilot_app.post("/accept_completion")
async def check_status(req: AcceptRequest):
    try:
        response = requests.post(f"{NODE_SERVER_URL}/sendNotification", json={"method": "notifyAccepted", "params": req.dict()})
        return {"message": 'Completion Accepted'}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

@copilot_app.post("/reject_completion")
async def check_status(req: RejectRequest):
    try:
        response = requests.post(f"{NODE_SERVER_URL}/sendNotification", json={"method": "notifyRejected", "params": req.dict()})
        return {"message": 'Completion Rejected'}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))
    