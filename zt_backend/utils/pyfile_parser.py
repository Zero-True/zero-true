import ast
import inspect
import textwrap
import os
import importlib.util
from collections import OrderedDict, defaultdict
from pathlib import Path
from uuid import uuid4
from zt_backend.models.notebook import Notebook, CodeCell
import astroid
from zt_backend.runner.code_cell_parser import (
    get_imports,
    get_defined_names,
    get_loaded_names,
    get_loaded_modules,
    get_functions,
)
def parse_cell(func):
    """
    Inspect the function to detect:
      - The function name (the cell_id).
      - Whether its *only* statement is one of zt.sql(...), zt.markdown(...), or zt.text(...).
      - If so, store only that string argument in cell_obj.code.
      - Otherwise, store the full code block in cell_obj.code, excluding all return statements.
      - Includes nested function definitions.
    """
    WRAPPER_TO_TYPE = {"sql": "sql", "markdown": "markdown", "text": "text"}

    source = inspect.getsource(func)
    source = textwrap.dedent(source)
    tree = ast.parse(source)

    func_def = None
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            func_def = node
            break

    if not func_def:
        raise ValueError(f"No function definition found in {func.__name__}")

    cell_id = func_def.name
    cell_type = "code"  # default

    def filter_return_statements(node):
        """Recursively remove trivial returns from function bodies."""
        if isinstance(node, ast.FunctionDef):
            node.body = [filter_return_statements(subnode) for subnode in node.body if not (isinstance(subnode, ast.Return) and not subnode.value)]
        elif isinstance(node, ast.Module):
            node.body = [filter_return_statements(subnode) for subnode in node.body]
        return node

    # Remove trivial returns from the function body
    filtered_tree = filter_return_statements(func_def)
    meaningful_body = filtered_tree.body

    if len(meaningful_body) == 1 and isinstance(meaningful_body[0], ast.Expr):
        expr_node = meaningful_body[0].value
        if (
            isinstance(expr_node, ast.Call)
            and isinstance(expr_node.func, ast.Attribute)
            and isinstance(expr_node.func.value, ast.Name)
            and expr_node.func.value.id == "zt"
        ):
            # This is zt.<something>(...)
            wrapper_name = expr_node.func.attr
            if wrapper_name in WRAPPER_TO_TYPE:
                cell_type = WRAPPER_TO_TYPE[wrapper_name]
                # If there's exactly one arg and it's a string, store only that string
                if expr_node.args and isinstance(expr_node.args[0], ast.Constant):
                    return cell_id, expr_node.args[0].value, cell_type

    # Otherwise, gather the entire code block as multi-line code (excluding all return statements)
    code_lines = []
    for subnode in meaningful_body:
        segment = ast.get_source_segment(source, subnode)
        if segment and segment.strip():
            code_lines.append(segment)

    final_code = "\n".join(code_lines)
    return cell_id, final_code, cell_type



def cell(func, hidden=False, type='code', hide_code=False, expand_code=False,
         show_table=False, non_reactive=False, cell_name=None,variable_name=""):
    """
    Create a CodeCell from a function object, plus metadata.
    We rely on parse_cell(...) to see if the function calls zt.sql, zt.markdown, etc.
    If it's a single wrapper call, we store only the string argument in .code.
    Otherwise, we store the entire block of code.
    """
    cell_id, raw_code, detected_type = parse_cell(func)
    var_name = variable_name
    # If parse_cell found e.g. 'sql', 'markdown', or 'text', override 'type'
    final_type = detected_type if detected_type != 'code' else type
    return CodeCell(
        id=cell_id,
        code=raw_code,  # raw code or text
        output="",
        cellName=(cell_name or ""),
        hideCell=hidden,
        hideCode=hide_code,
        expandCode=expand_code,
        showTable=show_table,
        nonReactive=non_reactive,
        cellType=final_type,
        variable_name = var_name
    )


def notebook(id, name="Zero True", nonreactive=False, cells=None):
    """
    Create a structured Notebook object from a list of CodeCell or function references.
    """
    if cells is None:
        cells = []
    return Notebook(
        userId='',
        notebookId=id,
        notebookName=name,
        nonreactive=nonreactive,
        cells=OrderedDict((c.id, c) for c in cells)
    )


def load_notebook_from_file(file_path, notebook_variable_name="notebook"):
    """
    Load and execute a Python file, returning the named notebook variable.
    """
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if hasattr(module, notebook_variable_name):
        return getattr(module, notebook_variable_name)
    else:
        raise AttributeError(f"{notebook_variable_name} not found in {file_path}")


def update_notebook_file(filepath, notebook_obj):
    """
    Update or create a Python file to match the given Notebook’s cell definitions
    and *physically remove* the function definition for any cell that was deleted
    from the notebook.
    This version:
      - Keeps exactly one blank line before each cell (if needed).
      - Removes old functions if they've been removed from the notebook.
      - If a cell is recognized as markdown/sql/text, it writes zt.markdown(...), zt.sql(...), etc. in the file,
        but the notebook only loads the raw string (see parse_cell).
    """
    import re
    import_line = "import zero_true as zt\n"

    # Helper function to ensure at most one blank line
    def maybe_add_blank_line(line_list):
        if line_list and line_list[-1].strip():  # last line not empty
            line_list.append("\n")

    # Helper to build code block for each cell (in the file).
    def build_cell_code_block(fn_name, cell_obj, def_line):
        """
        If the cell is e.g. sql, we'll put "    zt.sql(\"\"\"...\")" in the file.
        Meanwhile, in the notebook data structure, .code contains only the raw query.
        """
        return_line = "    return"
        if cell_obj.cellType == 'code':
            try:
                module = astroid.parse(cell_obj.code)
                all_imports = get_imports(module)
                function_names, function_args = get_functions(module)
                defined_names = get_defined_names(module) + function_names
                loaded_names = (
                    get_loaded_names(module, defined_names)
                    + get_loaded_modules(module, all_imports)
                )
                # Optionally ensure uniqueness while preserving order
                seen = set()
                loaded_names_ordered = []
                for name in loaded_names:
                    if name not in seen:
                        seen.add(name)
                        loaded_names_ordered.append(name)
                loaded_names = loaded_names_ordered
            except Exception as e:
                print(f"[Warning] Could not parse code in cell '{fn_name}': {e}")
                loaded_names = []
                defined_names = []

            # 2) Build function signature (optional arguments)
            if loaded_names:
                def_line = f"def {fn_name}({', '.join(loaded_names)}):"
            if defined_names:
                return_line =f"    return({', '.join(defined_names)})"
        
        lines = [def_line]  # e.g. "def cell_0():"
        if cell_obj.cellType in ["markdown", "sql", "text"]:
            # Write zt.sql("""some code""") in the file
            lines.append(f"    zt.{cell_obj.cellType}(\"\"\"{cell_obj.code}\"\"\")")
        else:
            # For "code" cells, we just insert them line by line
            for raw in cell_obj.code.splitlines():
                lines.append(f"    {raw}")
        lines.append(return_line)
        return lines

    # 1) Read existing lines or init
    try:
        with open(filepath, 'r') as f:
            original_lines = f.readlines()
    except FileNotFoundError:
        original_lines = [import_line, "\n"]

    original_source = "".join(original_lines)
    print("ORIGINAL:\n", original_source)

    # 1a) Gather old_cell_ids by scanning lines for 'notebook=zt.notebook(..., cells=[zt.cell(...), ...])'
    def parse_cell_calls_from_notebook_line(line: str):
        collapsed = line.replace(" ", "").replace("\n", "")
        if "notebook=zt.notebook(" not in collapsed:
            return []
        pattern = r"cells=\[(.*?)\]"
        m = re.search(pattern, collapsed)
        if not m:
            return []
        inside = m.group(1)  # e.g. "zt.cell(a),zt.cell(b)"
        cell_pattern = r"zt\.cell\((.*?)\)"
        found = re.findall(cell_pattern, inside)
        ret = []
        for fcall in found:
            # first arg is before the first comma or end
            first_part = fcall.split(",")[0].strip().strip("'").strip('"')
            ret.append(first_part)
        return ret

    old_cell_ids = set()
    for line in original_lines:
        for cid in parse_cell_calls_from_notebook_line(line):
            old_cell_ids.add(cid)

    # 2) Parse the file’s AST => gather all top-level function definitions
    try:
        tree = ast.parse(original_source)
    except SyntaxError:
        # If the file is partially corrupt, parse only the import line
        tree = ast.parse(import_line)

    func_defs = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            start_line = node.lineno - 1
            end_line = node.end_lineno - 1
            fn_name = node.name
            func_defs.append((start_line, end_line, fn_name))

    func_defs.sort(key=lambda x: x[0])

    from collections import defaultdict
    fn_name_map = defaultdict(list)
    for (start_i, end_i, fn_name) in func_defs:
        fn_name_map[fn_name].append((start_i, end_i))

    new_cell_ids = set(notebook_obj.cells.keys())
    final_defs = []

    # 3) For each function name, check if it’s recognized as an old cell
    #   - If old cell but not in new => remove
    #   - If old cell & in new => keep last definition => rewrite
    #   - Otherwise => keep as random code
    for fn_name, ranges in fn_name_map.items():
        ranges.sort(key=lambda x: x[0])
        if fn_name in old_cell_ids:
            if fn_name not in new_cell_ids:
                # user deleted this cell => remove all definitions
                for (s_i, e_i) in ranges:
                    final_defs.append((s_i, e_i, "_REMOVE_", True))
            else:
                # keep last => rewrite; earlier are duplicates
                last_start, last_end = ranges[-1]
                final_defs.append((last_start, last_end, fn_name, True))
                for (s_i, e_i) in ranges[:-1]:
                    final_defs.append((s_i, e_i, "_DUPLICATE_", True))
        else:
            # not recognized as old cell => keep as non-cell code
            for (s_i, e_i) in ranges:
                final_defs.append((s_i, e_i, fn_name, False))

    final_defs.sort(key=lambda x: x[0])

    updated_lines = []
    current_idx = 0
    handled_cells = set()

    i = 0
    while i < len(final_defs):
        (start_i, end_i, fn_name, is_cell) = final_defs[i]

        # copy lines up to start_i
        while current_idx < start_i and current_idx < len(original_lines):
            updated_lines.append(original_lines[current_idx])
            current_idx += 1

        if fn_name == "_DUPLICATE_":
            current_idx = end_i + 1
            i += 1
            continue
        if fn_name == "_REMOVE_":
            current_idx = end_i + 1
            i += 1
            continue

        if is_cell:
            # This is a cell in both old and new => we rewrite
            if fn_name in new_cell_ids:
                cell_obj = notebook_obj.cells[fn_name]
                handled_cells.add(fn_name)
                def_line = original_lines[start_i].rstrip("\n")

                # Add at most one blank line before the new version
                maybe_add_blank_line(updated_lines)

                new_block = build_cell_code_block(fn_name, cell_obj, def_line)
                for ln in new_block:
                    updated_lines.append(ln + "\n")
            # Move on
            current_idx = end_i + 1
            i += 1
        else:
            # Non-cell code => keep as is
            while current_idx <= end_i and current_idx < len(original_lines):
                updated_lines.append(original_lines[current_idx])
                current_idx += 1
            i += 1

    # copy leftover lines
    while current_idx < len(original_lines):
        updated_lines.append(original_lines[current_idx])
        current_idx += 1

    # remove old notebook lines (the lines with "notebook=zt.notebook(...)")
    final_buf = []
    for line in updated_lines:
        if "notebook=zt.notebook(" in line.replace(" ", ""):
            continue
        final_buf.append(line)
    updated_lines = final_buf

    # Now add brand-new cells that didn't exist previously
    for cid, cobj in notebook_obj.cells.items():
        if cid not in handled_cells:
            # brand new cell
            maybe_add_blank_line(updated_lines)
            def_line = f"def {cid}():"
            new_block = build_cell_code_block(cid, cobj, def_line)
            for ln in new_block:
                updated_lines.append(ln + "\n")

    # Build the final notebook=zt.notebook(...) line
    def format_cell_call(fn_name, cobj):
        """
        zt.cell(fn_name, type='markdown', hidden=True, etc.)
        We only set arguments that differ from default.
        """
        call = f"zt.cell({fn_name}"
        # If cellType != 'code'
        if cobj.cellType in ["markdown", "sql", "text"]:
            call += f", type='{cobj.cellType}'"
        if cobj.hideCell:
            call += ", hidden=True"
        if cobj.hideCode:
            call += ", hide_code=True"
        if cobj.expandCode:
            call += ", expand_code=True"
        if cobj.showTable:
            call += ", show_table=True"
        if cobj.nonReactive:
            call += ", non_reactive=True"
        if cobj.variable_name:
            call += f", variable_name='{cobj.variable_name}'"
        if cobj.cellName:
            call += f", cell_name='{cobj.cellName}'"
        call += ")"
        return call

    nb_args = [f"id={notebook_obj.notebookId!r}"]
    if notebook_obj.notebookName != "Zero True":
        nb_args.append(f"name={notebook_obj.notebookName!r}")

    calls = []
    for cid in notebook_obj.cells:
        calls.append(format_cell_call(cid, notebook_obj.cells[cid]))
    nb_args.append("cells=[" + ", ".join(calls) + "]")

    final_line = "notebook = zt.notebook(" + ", ".join(nb_args) + ")\n"

    # Clean up trailing blank lines
    while updated_lines and not updated_lines[-1].strip():
        updated_lines.pop()

    # Ensure at most one blank line before the final line
    maybe_add_blank_line(updated_lines)
    updated_lines.append(final_line)

    # Make sure we end with a newline
    if not updated_lines[-1].endswith("\n"):
        updated_lines[-1] += "\n"

    # Ensure import line
    if not any("import zero_true as zt" in line for line in updated_lines):
        updated_lines.insert(0, "import zero_true as zt\n\n")

    print("UPDATED:\n", "".join(updated_lines))
    filepath_temp = filepath.replace('.py', str(uuid4()) + '.py')
    with open(filepath_temp, 'w') as f:
        f.writelines(updated_lines)
    os.replace(filepath_temp, filepath)
