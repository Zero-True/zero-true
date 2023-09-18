from zt_backend.runner.code_cell_parser import parse_cells, build_dependency_graph
import pytest

# Test 1: No dependencies between cells
def test_no_dependencies():
    cells = ["a = 1", "b = 2", "c = 3"]
    cell_dict = build_dependency_graph(parse_cells(cells))
    assert cell_dict[0]['defined_names'] == ['a'] and cell_dict[0]['loaded_names'] == [], "Test 1 Failed"
    assert cell_dict[1]['defined_names'] == ['b'] and cell_dict[1]['loaded_names'] == [], "Test 1 Failed"
    assert cell_dict[2]['defined_names'] == ['c'] and cell_dict[2]['loaded_names'] == [], "Test 1 Failed"

# Test 2: Simple dependencies
def test_simple_dependencies():
    cells = ["a = 1", "b = a + 2", "c = b + 3"]
    cell_dict = build_dependency_graph(parse_cells(cells))
    assert cell_dict[0]['defined_names'] == ['a'] and cell_dict[0]['loaded_names'] == [], "Test 2 Failed"
    assert cell_dict[1]['defined_names'] == ['b'] and cell_dict[1]['loaded_names'] == ['a'], "Test 2 Failed"
    assert cell_dict[2]['defined_names'] == ['c'] and cell_dict[2]['loaded_names'] == ['b'], "Test 2 Failed"

# Test 3: Complex dependencies
def test_complex_dependencies():
    cells = ["a = 1", "b = a + 2", "c = b + a"]
    cell_dict = build_dependency_graph(parse_cells(cells))
    assert cell_dict[0]['defined_names'] == ['a'] and cell_dict[0]['loaded_names'] == [], "Test 3 Failed"
    assert cell_dict[1]['defined_names'] == ['b'] and cell_dict[1]['loaded_names'] == ['a'], "Test 3 Failed"
    assert cell_dict[2]['defined_names'] == ['c'] and set(cell_dict[2]['loaded_names']) == set(['b', 'a']), "Test 3 Failed"

# Test 4: Overriding dependencies
def test_overriding_dependencies():
    cells = ["a = 1", "b = a + 2", "a = 3", "c = a + b"]
    cell_dict = build_dependency_graph(parse_cells(cells))
    assert cell_dict[0]['defined_names'] == ['a'] and cell_dict[0]['loaded_names'] == [], "Test 4 Failed"
    assert cell_dict[1]['defined_names'] == ['b'] and cell_dict[1]['loaded_names'] == ['a'], "Test 4 Failed"
    assert cell_dict[2]['defined_names'] == ['a'] and cell_dict[2]['loaded_names'] == [], "Test 4 Failed"
    assert cell_dict[3]['defined_names'] == ['c'] and set(cell_dict[3]['loaded_names']) == set(['a', 'b']), "Test 4 Failed"

# Test 5: Function definitions and calls
def test_function_definitions_and_calls():
    cells = ["def f(x): return x + 2", "a = f(2)", "b = a + 3"]
    cell_dict = build_dependency_graph(parse_cells(cells))
    assert cell_dict[0]['defined_names'] == ['f'] and cell_dict[0]['loaded_names'] == [], "Test 5 Failed"
    assert cell_dict[1]['defined_names'] == ['a'] and cell_dict[1]['loaded_names'] == ['f'], "Test 5 Failed"

# Test 6: Dependencies with function calls and redefinitions
def test_dependencies_with_function_calls_and_redefinitions():
    cells = ["def f(x): return x + 2", "a = f(2)", "b = a + 3", "def g(x): return x * 2", "c = g(b)"]
    cell_dict = build_dependency_graph(parse_cells(cells))
    assert cell_dict[0]['defined_names'] == ['f'] and cell_dict[0]['loaded_names'] == [], "Test 6 Failed"
    assert cell_dict[1]['defined_names'] == ['a'] and cell_dict[1]['loaded_names'] == ['f'], "Test 6 Failed"
    assert cell_dict[2]['defined_names'] == ['b'] and cell_dict[2]['loaded_names'] == ['a'], "Test 6 Failed"
    assert cell_dict[3]['defined_names'] == ['g'] and cell_dict[3]['loaded_names'] == [], "Test 6 Failed"
    assert cell_dict[4]['defined_names'] == ['c'] and set(cell_dict[4]['loaded_names']) == set(['g', 'b']), "Test 6 Failed"

# Test 7: Importing a module in one cell and using it in another
def test_importing_module():
    cells = ["import math", "a = math.sqrt(4)"]
    cell_dict = build_dependency_graph(parse_cells(cells))
    assert cell_dict[0]['defined_names'] == ['math'] and cell_dict[0]['loaded_names'] == [], "Test 7 Failed"
    assert cell_dict[1]['defined_names'] == ['a'] and cell_dict[1]['loaded_names'] == ['math'], "Test 7 Failed"

# Test 8: Defining multiple variables in one cell
def test_multiple_variables_in_one_cell():
    cells = ["a = 1; b = 2; c = 3", "d = a + b + c"]
    cell_dict = build_dependency_graph(parse_cells(cells))
    assert set(cell_dict[0]['defined_names']) == set(['a', 'b', 'c']) and cell_dict[0]['loaded_names'] == [], "Test 8 Failed"
    assert cell_dict[1]['defined_names'] == ['d'] and set(cell_dict[1]['loaded_names']) == set(['a', 'b', 'c']), "Test 8 Failed"

# Test 9: Multiline cells
def test_multiline_cells():
    cells = ["a = 1\nb = 2\nc = 3", "d = a + b\ne = c * d"]
    cell_dict = build_dependency_graph(parse_cells(cells))
    assert set(cell_dict[0]['defined_names']) == set(['a', 'b', 'c']) and cell_dict[0]['loaded_names'] == [], "Test 9 Failed"
    assert set(cell_dict[1]['defined_names']) == set(['d', 'e']) and set(cell_dict[1]['loaded_names']) == set(['a', 'b', 'c']), "Test 9 Failed"

# Test 10: Importing a module with an alias in one cell and using it in another
def test_importing_module_with_alias():
    cells = ["import math as m", "a = m.sqrt(4)"]
    cell_dict = build_dependency_graph(parse_cells(cells))
    assert cell_dict[0]['defined_names'] == ['m'] and cell_dict[0]['loaded_names'] == [], "Test 10 Failed"
    assert cell_dict[1]['defined_names'] == ['a'] and cell_dict[1]['loaded_names'] == ['m'], "Test 10 Failed"
