from io import StringIO
from contextlib import redirect_stdout
from zt_backend.models import request, response
from zt_backend.models.components.zt_component import ZTComponent
from zt_backend.models.state import component_values, created_components, context_globals

def execute_request(request: request.Request):
    context_globals['exec_mode'] = True
    cell_outputs = []
    component_values.update(request.components)
    component_globals={'global_state': component_values}
    added_components = []
    for code_cell in request.cells:
        f = StringIO()
        with redirect_stdout(f):
            try:
                exec(code_cell.code, component_globals)
            except Exception as e:
                print(e)
        response_components = []
        for component_name, value in component_globals.items():
            if isinstance(value, ZTComponent) and value.id not in added_components:
                value.variable_name = component_name
                added_components.append(value.id)
                response_components.append(value)
        cell_outputs.append(response.CellResponse(id=code_cell.id, components=response_components, output=f.getvalue()))
    component_values.clear()
    created_components.clear()
    context_globals['exec_mode'] = False
    return response.Response(cells=cell_outputs)