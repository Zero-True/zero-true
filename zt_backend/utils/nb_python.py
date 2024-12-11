
from typing import OrderedDict
from zt_backend.models.state.user_state import UserState
from zt_backend.models.state.notebook_state import NotebookState
from zt_backend.models.api import request, response
from zt_backend.models import notebook
from zt_backend.utils.debounce import debounce
from zt_backend.config import settings
from pathlib import Path
import logging
import duckdb
import uuid
import os
import traceback
import json
import copy
import rtoml
import ast
import re
import importlib
import textwrap

logger = logging.getLogger("__name__")



def parse_function(code_str):
    lines = code_str.strip('\n').split('\n')
    
    # Find the definition lines (def line may span multiple lines until we hit a closing ')')
    def_lines = []
    found_def = False
    for line in lines:
        if not found_def and line.strip().startswith('def '):
            found_def = True
        if found_def:
            def_lines.append(line)
            if ')' in line:
                break
    
    # Combine definition lines and find first '(' and last ')'
    combined = ' '.join(def_lines)
    start = combined.find('(')
    end = combined.rfind(')')
    
    # Extract and parse arguments
    arg_str = combined[start+1:end].strip()
    args_dict = {}
    if arg_str:
        for arg in arg_str.split(','):
            name, val = arg.strip().split('=')
            args_dict[name.strip()] = val.strip()
    
    # Find where definition ended and body begins
    def_end_line = 0
    for i, line in enumerate(lines):
        if line in def_lines and ')' in line:
            def_end_line = i + 1
            break

    #remove function wrapper from code in case of sql, python, markdown
    if args_dict["cell_type"] in ["'sql'","'markdown'","'text'"]:
        print('hello')
        line_start=1
        line_end=-2
    else:
        line_start=0
        line_end=0
    # Dedent the body
    body = textwrap.dedent('\n'.join(lines[def_end_line+line_start:-1+line_end]))

    return args_dict, body



def parse_notebook_file(notebook_path):
    """
    Parses a Python notebook file and reconstructs its metadata and cells.
    """
    if os.path.exists(notebook_path):
        try: 
            with notebook_path.open("r", encoding="utf-8") as project_file:
                    python_code = project_file.read()
            # Extract notebook-level metadata
            notebook_id_match = re.search(r'notebook_id\s*=\s*["\'](.*?)["\']', python_code)
            notebook_name_match = re.search(r'notebook_name\s*=\s*["\'](.*?)["\']', python_code)
            notebook_id = notebook_id_match.group(1) if notebook_id_match else None
            notebook_name = notebook_name_match.group(1) if notebook_name_match else "Zero True"

            # Split on cell definitions

            # The regex uses `^` (start of line, multiline) to ensure only top-level `def cell(id=...` are split on
            cell_blocks = re.split(r'(?m)^def cell\(id=', python_code)[1:]

            cells = {}

            for block in cell_blocks:
                print(block)
                args,body=parse_function("def cell(id="+block)
                cell_id=args.get('id').replace('"','').replace("'",'')
                # Construct the cell object
                cells[cell_id] = {
                    "id": cell_id,
                    "cellName": args.get("cell_name", ""),
                    "cellType": args.get("cell_type", "python").replace('"','').replace("'",''),
                    "hideCell": args.get("hide_cell", False),
                    "hideCode": args.get("hide_code", False),
                    "expandCode": args.get("expand_code", False),
                    "showTable": args.get("show_table", False),
                    "nonReactive": args.get("non_reactive", False),
                    "code": body,
                    "output":"",
                    "comments": {},
                }

            return {
                "userId":'',
                "notebookId": notebook_id,
                "notebookName": notebook_name,
                "cells": cells,
            }

        except Exception as e:
            print("Error parsing notebook file:", traceback.format_exc())
            raise
    else:
        return(None)



def write_notebook_to_python(notebook_state):
    tmp_uuid_file = Path(settings.zt_path) / f"notebook_{uuid.uuid4()}.py"
    notebook_path = Path(settings.zt_path) / "notebook.py"
    logger.debug("Saving Python file for notebook %s", notebook_state.zt_notebook.notebookId)

    try:
        with tmp_uuid_file.open("w", encoding="utf-8") as py_file:
            #import zero-true etc.
            py_file.write("import zero_true as zt\n")
            py_file.write("from zero_true import cell, md, html, sql\n\n")

            # Notebook-level metadata
            py_file.write("# Notebook Metadata\n")
            py_file.write(f'notebook_id = "{notebook_state.zt_notebook.notebookId}"\n')
            py_file.write(f'notebook_name = "{notebook_state.zt_notebook.notebookName}"\n\n')

            # Include default metadata for reference
            py_file.write("# Default metadata values:\n")
            py_file.write("DEFAULT_METADATA = {\n")
            py_file.write("    'cell_type': 'python',\n")
            py_file.write("    'hide_cell': False,\n")
            py_file.write("    'hide_code': False,\n")
            py_file.write("    'expand_code': False,\n")
            py_file.write("    'show_table': False,\n")
            py_file.write("    'non_reactive': False,\n")
            py_file.write("}\n\n")

            for cell_id, cell in notebook_state.zt_notebook.cells.items():
                # Define the cell function
                py_file.write(f'def cell(id= "{cell_id}", ')

                # Only include metadata arguments if they deviate from defaults
                metadata_args = []
                if cell.cellType != "python":
                    metadata_args.append(f"cell_type='{cell.cellType}'")
                if cell.hideCell:
                    metadata_args.append(f"hide_cell={cell.hideCell}")
                if cell.hideCode:
                    metadata_args.append(f"hide_code={cell.hideCode}")
                if cell.expandCode:
                    metadata_args.append(f"expand_code={cell.expandCode}")
                if cell.showTable:
                    metadata_args.append(f"show_table={cell.showTable}")
                if cell.nonReactive:
                    metadata_args.append(f"non_reactive={cell.nonReactive}")
                if cell.cellName:
                    metadata_args.append(f"cell_name={cell.cellName}")
                
         
                # Join metadata arguments for the function signature
                py_file.write(", ".join(metadata_args))
                py_file.write("):\n")

                #add function wrapper if cell is markdown or SQL
                if cell.cellType=='sql':
                    py_file.write('    sql("""\n')
                    extra_line='    """)\n'
                if cell.cellType=='markdown':
                    py_file.write('    md("""\n')
                    extra_line='    """)\n'
                if cell.cellType=='text':
                    py_file.write('    text("""\n')
                    extra_line='    """)\n'
                if cell.cellType=='code':
                    extra_line = '' 
                # Add the actual code
                code_lines = cell.code.split("\n")
                for line in code_lines:
                    py_file.write(f"    {line}\n")
                if extra_line!='':
                    py_file.write(extra_line+'\n')
                py_file.write('    return\n')

                # Add comments as inline Python comments
                if cell.comments:
                    py_file.write("\n    # Comments for this cell\n")
                    for comment_id, comment in cell.comments.items():
                        py_file.write(f"    # {comment_id}: {comment.comment} (Resolved: {comment.resolved})\n")
                        for reply_id, reply in comment.replies.items():
                            py_file.write(f"    # Reply {reply_id}: {reply.comment}\n")

                py_file.write("\n")  # Separate cells by a blank line

        tmp_uuid_file.replace(notebook_path)
    except Exception as e:
        logger.error(
            "Error saving notebook %s Python file: %s",
            notebook_state.zt_notebook.notebookId,
            traceback.format_exc(),
        )

    finally:
        try:
            tmp_uuid_file.unlink()
        except Exception:
            logger.debug(
                "Error while deleting temporary Python file for notebook %s: %s",
                notebook_state.zt_notebook.notebookId,
                traceback.format_exc(),
            )
            pass
    logger.debug("Python file saved for notebook %s", notebook_state.zt_notebook.notebookId)

