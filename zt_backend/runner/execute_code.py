from io import StringIO
from contextlib import redirect_stdout
from zt_backend.models import request, response
from zt_backend.models.components.zt_component import ZTComponent
from zt_backend.models.state import global_state



def execute_request(request: request.Request):
    cell_outputs = []
    global_state.update(request.components)
    component_globals={'global_state': global_state}

    for code_cell in request.cells:
        cell_outputs.append(execute_code(code_cell, component_globals))
    return response.Response(cells=cell_outputs)

def execute_code(code_cell: request.CodeRequest, component_globals):
    f = StringIO()
    with redirect_stdout(f):
        exec(code_cell.code, component_globals)
    global_state.clear()
    response_components = []
    for component_name, value in component_globals.items():
        if isinstance(value, ZTComponent):
            value.variable_name = component_name
            response_components.append(value)
    return response.CellResponse(id=code_cell.id, components=response_components, output=f.getvalue())
        

