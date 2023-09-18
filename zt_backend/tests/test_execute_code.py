from zt_backend.runner.execute_code import execute_request, cell_outputs_dict
from zt_backend.models.request import Request, CodeRequest

# Initialize or clear cell_outputs_dict
def setup_function():
    cell_outputs_dict.clear()

# Test for simple variable assignment
def test_execute_request_simple_variable():
    setup_function()
    req = Request(originId="0", cells=[CodeRequest(id="0", code="a = 1")], components={})
    execute_request(req)
    assert 'a' in cell_outputs_dict['0']
    assert cell_outputs_dict['0']['a'] == 1

# Test for function definition
def test_execute_request_function_definition():
    setup_function()
    req = Request(originId="1", cells=[CodeRequest(id="1", code="def add(x, y): return x + y")], components={})
    execute_request(req)
    assert 'add' in cell_outputs_dict['1']

# Test for importing modules
def test_execute_request_import_module():
    setup_function()
    req = Request(originId="2", cells=[CodeRequest(id="2", code="import math")], components={})
    execute_request(req)
    assert 'math' in cell_outputs_dict['2']

# Test for multiple cells with dependencies
def test_execute_request_multiple_cells_with_dependencies():
    setup_function()
    req = Request(originId="3", cells=[CodeRequest(id="3", code="a = 1"),
                         CodeRequest(id="4", code="b = a + 1")], components={})
    execute_request(req)
    assert 'a' in cell_outputs_dict['3']
    assert 'b' in cell_outputs_dict['4']
    assert cell_outputs_dict['3']['a'] == 1
    assert cell_outputs_dict['4']['b'] == 2
