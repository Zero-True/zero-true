from zt_backend.runner.execute_code import execute_request
from zt_backend.runner.user_state import UserState
from zt_backend.models.request import Request, CodeRequest
from unittest.mock import Mock, AsyncMock
import threading

notebook_state=UserState('')
websocket = Mock()
websocket.send_json = AsyncMock()

# Initialize or clear cell_outputs_dict
def setup_function():
    notebook_state=UserState('')
    notebook_state.websocket = websocket

# Test for simple variable assignment
def test_execute_request_simple_variable():
    setup_function()
    req = Request(originId="0", cells=[CodeRequest(id="0", code="a = 1", variable_name="", cellType='code')], components={})
    execute_thread = threading.Thread(target=execute_request, args=(req, notebook_state, websocket))
    execute_thread.start()
    execute_thread.join()
    assert 'a' in notebook_state.cell_outputs_dict['0']
    assert notebook_state.cell_outputs_dict['0']['a'] == 1

# Test for function definition
def test_execute_request_function_definition():
    setup_function()
    req = Request(originId="1", cells=[CodeRequest(id="1", code="def add(x, y): return x + y", variable_name="", cellType='code')], components={})
    execute_thread = threading.Thread(target=execute_request, args=(req, notebook_state, websocket))
    execute_thread.start()
    execute_thread.join()
    assert 'add' in notebook_state.cell_outputs_dict['1']

# Test for importing modules
def test_execute_request_import_module():
    setup_function()
    req = Request(originId="2", cells=[CodeRequest(id="2", code="import math", variable_name="", cellType='code')], components={})
    execute_thread = threading.Thread(target=execute_request, args=(req, notebook_state, websocket))
    execute_thread.start()
    execute_thread.join()
    assert 'math' in notebook_state.cell_outputs_dict['2']

# Test for multiple cells with dependencies
def test_execute_request_multiple_cells_with_dependencies():
    setup_function()
    req = Request(originId="3", cells=[CodeRequest(id="3", code="a = 1", variable_name="", cellType='code'),
                        CodeRequest(id="4", code="b = a + 1", variable_name="", cellType='code')], components={})
    execute_thread = threading.Thread(target=execute_request, args=(req, notebook_state, websocket))
    execute_thread.start()
    execute_thread.join()
    assert 'a' in notebook_state.cell_outputs_dict['3']
    assert 'b' in notebook_state.cell_outputs_dict['4']
    assert notebook_state.cell_outputs_dict['3']['a'] == 1
    assert notebook_state.cell_outputs_dict['4']['b'] == 2
