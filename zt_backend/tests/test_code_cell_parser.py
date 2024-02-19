from zt_backend.runner.code_cell_parser import parse_cells, build_dependency_graph
from zt_backend.models.request import Request,CodeRequest

# Test 1: No dependencies between cells
def test_no_dependencies():
    cells = Request(originId="0", cells=[CodeRequest(id="0",code="a = 1", variable_name="",  nonReactive=False, cellType='code'),
                           CodeRequest(id="1",code="b = 2", variable_name="",  nonReactive=False, cellType='code'),
                           CodeRequest(id="2",code="c = 3", variable_name="",  nonReactive=False, cellType='code')],\
                    components={"":""})
    cell_dict = build_dependency_graph(parse_cells(cells))
    assert cell_dict.cells['0'].defined_names == ['a'] and cell_dict.cells['0'].loaded_names == [], "Test 1 Failed"
    assert cell_dict.cells['1'].defined_names == ['b'] and cell_dict.cells['1'].loaded_names == [], "Test 1 Failed"
    assert cell_dict.cells['2'].defined_names == ['c'] and cell_dict.cells['2'].loaded_names == [], "Test 1 Failed"

# Test 2: Simple dependencies
def test_simple_dependencies():
    cells = Request(originId="0", cells=[CodeRequest(id="0", code="a = 1", variable_name="",  nonReactive=False, cellType='code'),
                           CodeRequest(id="1", code="b = a + 2", variable_name="",  nonReactive=False, cellType='code'),
                           CodeRequest(id="2", code="c = b + 3", variable_name="",  nonReactive=False, cellType='code')],
                    components={})
    cell_dict = build_dependency_graph(parse_cells(cells))
    
    assert cell_dict.cells['0'].defined_names == ['a'] and cell_dict.cells['0'].loaded_names == [], "Test 2 Failed"
    assert cell_dict.cells['1'].defined_names == ['b'] and cell_dict.cells['1'].loaded_names == ['a'], "Test 2 Failed"
    assert cell_dict.cells['2'].defined_names == ['c'] and cell_dict.cells['2'].loaded_names == ['b'], "Test 2 Failed"

# Test 3: Complex dependencies
def test_complex_dependencies():
    cells = Request(originId="0", cells=[CodeRequest(id="0", code="a = 1", variable_name="",  nonReactive=False, cellType='code'),
                           CodeRequest(id="1", code="b = a + 2", variable_name="",  nonReactive=False, cellType='code'),
                           CodeRequest(id="2", code="c = b + a", variable_name="",  nonReactive=False, cellType='code')],
                    components={})
    cell_dict = build_dependency_graph(parse_cells(cells))
    
    assert cell_dict.cells['0'].defined_names == ['a'] and cell_dict.cells['0'].loaded_names == [], "Test 3 Failed"
    assert cell_dict.cells['1'].defined_names == ['b'] and cell_dict.cells['1'].loaded_names == ['a'], "Test 3 Failed"
    assert cell_dict.cells['2'].defined_names == ['c'] and set(cell_dict.cells['2'].loaded_names) == set(['b', 'a']), "Test 3 Failed"

# Test 4: Overriding dependencies
def test_overriding_dependencies():
    cells = Request(originId="0", cells=[CodeRequest(id="0", code="a = 1", variable_name="",  nonReactive=False, cellType='code'),
                           CodeRequest(id="1", code="b = a + 2", variable_name="",  nonReactive=False, cellType='code'),
                           CodeRequest(id="2", code="a = 3", variable_name="",  nonReactive=False, cellType='code'),
                           CodeRequest(id="3", code="c = a + b", variable_name="",  nonReactive=False, cellType='code')],
                    components={})
    cell_dict = build_dependency_graph(parse_cells(cells))
    
    assert cell_dict.cells['0'].defined_names == ['a'] and cell_dict.cells['0'].loaded_names == [], "Test 4 Failed"
    assert cell_dict.cells['1'].defined_names == ['b'] and cell_dict.cells['1'].loaded_names == ['a'], "Test 4 Failed"
    assert cell_dict.cells['2'].defined_names == ['a'] and cell_dict.cells['2'].loaded_names == [], "Test 4 Failed"
    assert cell_dict.cells['3'].defined_names == ['c'] and set(cell_dict.cells['3'].loaded_names) == set(['a', 'b']), "Test 4 Failed"

# Test 5: Function definitions and calls
def test_function_definitions_and_calls():
    cells = Request(originId="0", cells=[CodeRequest(id="0", code="def f(x): return x + 2", variable_name="",  nonReactive=False, cellType='code'),
                           CodeRequest(id="1", code="a = f(2)", variable_name="",  nonReactive=False, cellType='code'),
                           CodeRequest(id="2", code="b = a + 3", variable_name="",  nonReactive=False, cellType='code')],
                    components={})
    cell_dict = build_dependency_graph(parse_cells(cells))
    
    assert cell_dict.cells['0'].defined_names == ['f'] and cell_dict.cells['0'].loaded_names == [], "Test 5 Failed"
    assert cell_dict.cells['1'].defined_names == ['a'] and cell_dict.cells['1'].loaded_names == ['f'], "Test 5 Failed"
    assert cell_dict.cells['2'].defined_names == ['b'] and cell_dict.cells['2'].loaded_names == ['a'], "Test 5 Failed"

# Test 6: Dependencies with function calls and redefinitions
def test_dependencies_with_function_calls_and_redefinitions():
    cells = Request(originId="0", cells=[CodeRequest(id="0", code="def f(x): return x + 2", variable_name="",  nonReactive=False, cellType='code'),
                           CodeRequest(id="1", code="a = f(2)", variable_name="",  nonReactive=False, cellType='code'),
                           CodeRequest(id="2", code="b = a + 3", variable_name="",  nonReactive=False, cellType='code'),
                           CodeRequest(id="3", code="def g(x): return x * 2", variable_name="",  nonReactive=False, cellType='code'),
                           CodeRequest(id="4", code="c = g(b)", variable_name="",  nonReactive=False, cellType='code')],
                    components={})
    cell_dict = build_dependency_graph(parse_cells(cells))
    
    assert cell_dict.cells['0'].defined_names == ['f'] and cell_dict.cells['0'].loaded_names == [], "Test 6 Failed"
    assert cell_dict.cells['1'].defined_names == ['a'] and cell_dict.cells['1'].loaded_names == ['f'], "Test 6 Failed"
    assert cell_dict.cells['2'].defined_names == ['b'] and cell_dict.cells['2'].loaded_names == ['a'], "Test 6 Failed"
    assert cell_dict.cells['3'].defined_names == ['g'] and cell_dict.cells['3'].loaded_names == [], "Test 6 Failed"
    assert cell_dict.cells['4'].defined_names == ['c'] and set(cell_dict.cells['4'].loaded_names) == set(['g', 'b']), "Test 6 Failed"

# Test 7: Importing a module in one cell and using it in another
def test_importing_module():
    cells = Request(originId="0", cells=[CodeRequest(id="0", code="import math", variable_name="",  nonReactive=False, cellType='code'),
                           CodeRequest(id="1", code="a = math.sqrt(4)", variable_name="",  nonReactive=False, cellType='code')],
                    components={})
    cell_dict = build_dependency_graph(parse_cells(cells))
    
    assert cell_dict.cells['0'].imported_modules == ['math'] and cell_dict.cells['0'].loaded_names == [], "Test 7 Failed"
    assert cell_dict.cells['1'].defined_names == ['a'] and cell_dict.cells['1'].loaded_modules == ['math'], "Test 7 Failed"

# Test 8: Defining multiple variables in one cell
def test_multiple_variables_in_one_cell():
    cells = Request(originId="0", cells=[CodeRequest(id="0", code="a = 1; b = 2; c = 3", variable_name="",  nonReactive=False, cellType='code'),
                           CodeRequest(id="1", code="d = a + b + c", variable_name="",  nonReactive=False, cellType='code')],
                    components={})
    cell_dict = build_dependency_graph(parse_cells(cells))
    
    assert set(cell_dict.cells['0'].defined_names) == set(['a', 'b', 'c']) and cell_dict.cells['0'].loaded_names == [], "Test 8 Failed"
    assert cell_dict.cells['1'].defined_names == ['d'] and set(cell_dict.cells['1'].loaded_names) == set(['a', 'b', 'c']), "Test 8 Failed"

# Test 9: Multiline cells
def test_multiline_cells():
    cells = Request(originId="0", cells=[CodeRequest(id="0", code="a = 1\nb = 2\nc = 3", variable_name="",  nonReactive=False, cellType='code'),
                           CodeRequest(id="1", code="d = a + b\ne = c * d", variable_name="",  nonReactive=False, cellType='code')],
                    components={})
    cell_dict = build_dependency_graph(parse_cells(cells))
    
    assert set(cell_dict.cells['0'].defined_names) == set(['a', 'b', 'c']) and cell_dict.cells['0'].loaded_names == [], "Test 9 Failed"
    print(cell_dict)
    assert set(cell_dict.cells['1'].defined_names) == set(['d', 'e']) and set(cell_dict.cells['1'].loaded_names) == set(['a', 'b', 'c','d']), "Test 9a Failed"

# Test 10: Importing a module with an alias in one cell and using it in another
def test_importing_module_with_alias():
    cells = Request(originId="0", cells=[CodeRequest(id="0", code="import math as m", variable_name="",  nonReactive=False, cellType='code'),
                           CodeRequest(id="1", code="a = m.sqrt(4)", variable_name="",  nonReactive=False, cellType='code')],
                    components={})
    cell_dict = build_dependency_graph(parse_cells(cells))
    
    assert cell_dict.cells['0'].imported_modules == ['m'] and cell_dict.cells['0'].loaded_names == [], "Test 10 Failed"
    assert cell_dict.cells['1'].defined_names == ['a'] and cell_dict.cells['1'].loaded_modules == ['m'], "Test 10 Failed"

# Test 11: SQL cell with dependency
def test_sql_cell():
    cells =  Request(originId="0", cells=[CodeRequest(id="0", code="a=1", variable_name="",  nonReactive=False, cellType='code'),
                                          CodeRequest(id="1", code="SELECT {a}", variable_name="df",  nonReactive=False, cellType='sql'),
                                            CodeRequest(id="2", code="print(df)", variable_name="",  nonReactive=False, cellType='code')],
                    components={})
    cell_dict = build_dependency_graph(parse_cells(cells))
    print(cell_dict)
    assert set(cell_dict.cells['1'].defined_names) == set(['conn','df']), "Test 11 Failed"
    assert cell_dict.cells['2'].defined_names == [], "Test 12 Failed" 
    assert set(cell_dict.cells['2'].loaded_names) == set(['print','df']), "Test 13 Failed"
    
