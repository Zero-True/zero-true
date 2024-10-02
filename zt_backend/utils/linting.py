import asyncio
import json
from typing import Dict, List
import logging
from collections import defaultdict
import time

# Constants
DEBOUNCE_TIME = 0.5  # seconds
RUFF_COMMAND = ['ruff', 'check', '--output-format=json', '-']

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Debounce settings
last_run_time = defaultdict(float)
pending_tasks: Dict[str, asyncio.Task] = {}

async def run_ruff_linting(text: str) -> List[Dict]:
    process = await asyncio.create_subprocess_exec(
        *RUFF_COMMAND,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate(input=text.encode())
    
    if stderr:
        logger.error(f"Error running Ruff: {stderr.decode()}")
        return []

    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        logger.error(f"Error decoding Ruff output: {stdout.decode()}")
        return []

def get_severity(code: str) -> str:
    """Determine the severity based on the error code."""
    if not code:
        return 'error'  # Treat empty codes as syntax errors
    
    severity_map = {
        'E': 'error',
        'F': 'error',
        'W': 'warning',
        'P': 'warning', 
        'C': 'info',  # Convention
        'N': 'info',  # Naming
        'Q': 'info',  # Quote style
        'T': 'warning',  # Type hinting issues
        'R': 'info',  # Refactoring suggestions
        'S': 'warning',  # Security issues
    }
    
    # Special handling for F8 series, excluding F82
    if code.startswith('F8') and not code.startswith('F82'):
        return 'warning'

    return severity_map.get(code[0], 'warning')

def transform_ruff_results(lint_errors: List[Dict], cell_line_count: int) -> List[Dict]:
    transformed_messages = []
    for message in lint_errors:
        try:
            code = message.get('code', '')
            severity = get_severity(code)
            
            # Adjust line numbers for CodeMirror (0-based)
            from_line = max(0, message["location"]["row"] - 1)
            to_line = max(0, message["end_location"]["row"] - 1 if "end_location" in message else message["location"]["row"] - 1)
            
            # Ensure line numbers don't exceed the cell's line count
            from_line = min(from_line, cell_line_count - 1)
            to_line = min(to_line, cell_line_count - 1)
            
            transformed_message = {
                "from": {
                    "line": from_line,
                    "ch": max(0, message["location"]["column"] - 1)
                },
                "to": {
                    "line": to_line,
                    "ch": max(0, message["end_location"]["column"] - 1 if "end_location" in message else message["location"]["column"])
                },
                "severity": severity,
                "message": f"{message.get('message', 'Error')}"
            }
            transformed_messages.append(transformed_message)
        except KeyError as e:
            logger.error(f"Error processing linting message: {str(e)}. Message: {message}")
    return transformed_messages

async def queued_get_cell_linting(cell_id: str, text: str, code_w_context: str) -> Dict[str, List[Dict]]:
    try:
        context_lines = code_w_context.split('\n')
        cell_lines = text.split('\n')
        cell_start_line = context_lines.index(cell_lines[0])

        # Prepare context-aware cell text
        preceding_context = '\n'.join(context_lines[:cell_start_line])
        context_aware_cell_text = f"{preceding_context}\n{text}"

        # Run linting on the context-aware cell text
        lint_errors = await run_ruff_linting(context_aware_cell_text)
        logger.debug(f"Ruff output for cell {cell_id}: {json.dumps(lint_errors)}")

        # Filter out linting errors from the preceding context
        preceding_context_line_count = len(preceding_context.split('\n'))
        cell_lint_errors = [
            error for error in lint_errors
            if error["location"]["row"] > preceding_context_line_count
        ]

        # Adjust line numbers to be relative to the cell
        for error in cell_lint_errors:
            error["location"]["row"] -= preceding_context_line_count
            if "end_location" in error:
                error["end_location"]["row"] -= preceding_context_line_count

        # Transform results
        transformed_messages = transform_ruff_results(cell_lint_errors, len(cell_lines))
        return {cell_id: transformed_messages}
    except Exception as e:
        logger.error(f"Error processing linting for cell {cell_id}: {str(e)}", exc_info=True)
        return {cell_id: []}