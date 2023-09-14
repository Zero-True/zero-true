from io import StringIO
from contextlib import redirect_stdout
from zt_backend.models import request, response
from zt_backend.models.components.zt_component import ZTComponent
from zt_backend.models.state import global_state



def execute_request(request: request.Request):
    cell_outputs = []
    for code_cell in request.cells:
        component_varialbes = {"components": request.components}
        for component in component_varialbes['components']:
            global_state[component.id]=component.value
            print(component.value)
        component_varialbes['global_state']=global_state
        cell_outputs.append(execute_code(code_cell, component_varialbes))
    return response.Response(cells=cell_outputs)

def execute_code(code_cell: request.CodeRequest, component_variables):
    f = StringIO()
    with redirect_stdout(f):
        exec(code_cell.code, component_variables)
    global_state.clear()
    response_components = []
    for component_name, value in component_variables.items():
        if isinstance(value, ZTComponent):
            value.variable_name = component_name
            response_components.append(value)
    return response.CellResponse(id=code_cell.id, components=response_components, output=f.getvalue())
        

