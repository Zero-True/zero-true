from zt_backend.models.state.notebook_state import NotebookState
from zt_backend.models import notebook
import rtoml
import subprocess
from pathlib import Path

notebook_state = NotebookState()

IPYNB_PATH = Path(__file__).resolve().parent / "test_file.ipynb"
OUTPUT_PATH = Path(__file__).resolve().parent / "notebook.ztnb"
NOTEBOOK_PATH = Path(__file__).resolve().parent / "test_notebook.ztnb"

def test_ipynb_to_ztnb():

    convert = subprocess.Popen(
        ["zero-true", "jupyter-convert", IPYNB_PATH, OUTPUT_PATH]
    )
    convert.wait()

    with open(NOTEBOOK_PATH, "r", encoding="utf-8") as file:
        expected_data = rtoml.loads(file.read().replace("\\", "\\\\"))

    expected_notebook_data = {
        "notebookId": "test_id",
        "notebookName": expected_data.get("notebookName", "Zero True"),
        "userId": "",
        "cells": {
            f"{index}": notebook.CodeCell(id=f"{index}", **cell_data, output="")
            for index, (cell_id, cell_data) in enumerate(expected_data["cells"].items())
        },
    }
    expected_notebook = notebook.Notebook(**expected_notebook_data)

    with open(OUTPUT_PATH, "r", encoding="utf-8") as file:
        output_data = rtoml.loads(file.read().replace("\\", "\\\\"))

    output_notebook_data = {
        "notebookId": "test_id",
        "notebookName": output_data.get("notebookName", "Zero True"),
        "userId": "",
        "cells": {
            f"{index}": notebook.CodeCell(id=f"{index}", **cell_data, output="")
            for index, (cell_id, cell_data) in enumerate(output_data["cells"].items())
        },
    }
    output_notebook = notebook.Notebook(**output_notebook_data)

    assert expected_notebook == output_notebook