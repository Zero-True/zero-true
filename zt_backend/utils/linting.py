from typing import List, Dict, Union
import tempfile
import os
from pylint import epylint as lint
from fastapi import HTTPException
import json
import logging
from zt_backend.utils.debounce import LintingDebouncer

logger = logging.getLogger(__name__)

linting_debouncer = LintingDebouncer(wait_time=0.2)  # 200ms debounce time


async def debounced_get_cell_linting(cell_id: str, cell_code: str, context_code: str):
    """
    Debounced version of get_cell_linting
    """
    return await linting_debouncer.debounce(cell_id, get_cell_linting, cell_id, cell_code, context_code)


async def get_cell_linting(cell_id: str, cell_code: str, context_code: str) -> Dict[str, List[Dict[str, Union[int, str, Dict[str, int]]]]]:
    """
    Lint the provided Python code for a specific cell, considering the context, and return the linting results.

    Args:
        cell_id (str): The ID of the cell being linted.
        cell_code (str): The code of the specific cell to lint.
        context_code (str): The entire notebook code for context.

    Returns:
        Dict[str, List[Dict[str, Union[int, str, Dict[str, int]]]]]: Linting results as a dictionary with cell_id as key.
    """
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(context_code)
            temp_file_path = temp_file.name

        (pylint_stdout, _) = lint.py_run(
            f'{temp_file_path} --output-format=json',
            return_std=True
        )

        lint_output = pylint_stdout.getvalue()
        os.unlink(temp_file_path)

        if not lint_output:
            return {cell_id: []}

        lint_messages = json.loads(lint_output)
        
        # Filter lint messages to only include those relevant to the current cell
        cell_start_line = context_code.count('\n', 0, context_code.index(cell_code)) + 1
        cell_end_line = cell_start_line + cell_code.count('\n')
        
        cell_lint_messages = [
            msg for msg in lint_messages
            if cell_start_line <= msg['line'] <= cell_end_line
        ]
        
        transformed_messages = transform_pylint_messages(cell_lint_messages, cell_start_line)
        return {cell_id: transformed_messages}

    except Exception as e:
        logger.error(f"Linting error for cell {cell_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Linting error for cell {cell_id}: {str(e)}")

def transform_pylint_messages(pylint_messages: List[Dict], cell_start_line: int) -> List[Dict[str, Union[int, str, Dict[str, int]]]]:
    """
    Transform Pylint messages into a format suitable for the frontend, adjusting line numbers to be cell-relative.

    Args:
        pylint_messages (List[Dict]): List of Pylint messages.
        cell_start_line (int): The starting line number of the cell in the context.

    Returns:
        List[Dict[str, Union[int, str, Dict[str, int]]]]: List of transformed messages.
    """
    transformed_messages = []
    for message in pylint_messages:
        severity = map_severity(message["type"])
        transformed_message = {
            "from": {
                "line": message["line"] - cell_start_line,
                "ch": message["column"] - 1
            },
            "to": {
                "line": message["line"] - cell_start_line,
                "ch": message["column"]
            },
            "severity": severity,
            "message": message["message"]
        }
        transformed_messages.append(transformed_message)
    return transformed_messages

def map_severity(pylint_type: str) -> str:
    """
    Map Pylint message types to severity levels.

    Args:
        pylint_type (str): Pylint message type.

    Returns:
        str: Corresponding severity level.
    """
    severity_map = {
        "convention": "info",
        "refactor": "info",
        "warning": "warning",
        "error": "error",
        "fatal": "error"
    }
    return severity_map.get(pylint_type.lower(), "info")