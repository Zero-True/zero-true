from models import Request, CodeCell

def execute_request(request: Request):
    for code_cell in request.cells:
        execute_code(code_cell)

def execute_code(code_cell: CodeCell):
    exec(code_cell.code)

