from models import request

def execute_request(request: request.Request):
    for code_cell in request.cells:
        execute_code(code_cell)

def execute_code(code_cell: request.CodeCell):
    exec(code_cell.code)

