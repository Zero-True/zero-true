from zt_backend.models.state.notebook_state import NotebookState
import subprocess
from pathlib import Path
import os
import importlib.util

IPYNB_PATH = Path("zt_backend/tests/test_file.ipynb").resolve()
OUTPUT_PATH = Path("zt_backend/tests/notebook.py").resolve()
NOTEBOOK_PATH = Path("zt_backend/tests/test_notebook.py").resolve()

def dynamic_import(module_path):
    spec = importlib.util.spec_from_file_location("notebook_module", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def test_ipynb_to_ztnb():

    # Step 1: Convert the IPYNB file to a Python file
    convert = subprocess.Popen(
        ["zero-true", "jupyter-convert", IPYNB_PATH, OUTPUT_PATH]
    )
    convert.wait()

    # Step 2: Import the expected notebook from test_notebook.py
    from test_notebook import notebook as expected_notebook
    output_module = dynamic_import(OUTPUT_PATH)
    output_notebook = output_module.notebook
    # Step 3: Import the generated notebook from notebook.py
    expected_notebook.notebookId='0'
    output_notebook.notebookId='0'
    # Step 4: Assert that the generated notebook matches the expected notebook
    assert output_notebook == expected_notebook

    # Step 5: Clean up the generated file
    os.remove(OUTPUT_PATH)
