import asyncio
import json
from typing import Dict, List
import logging
from collections import defaultdict
import subprocess
from zt_backend.utils.debounce import async_debounce
from fastapi.websockets import WebSocket

# Constants
DEBOUNCE_TIME = 0.5  # seconds
RUFF_COMMAND = [
    "ruff",
    "check",
    "--output-format=json",
    "--extend-ignore=E402",  # Ignore import position errors
    "-",
]

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Debounce settings
last_run_time = defaultdict(float)
pending_tasks: Dict[str, asyncio.Task] = {}


async def run_ruff_linting(text: str) -> List[Dict]:
    process = subprocess.Popen(
        RUFF_COMMAND,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout, stderr = process.communicate(input=text)

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
        return "error"  # Treat empty codes as syntax errors

    if code == "F401":
        return "warning"

    # Special handling for F8 series, excluding F82
    if code.startswith("F8") and not code.startswith("F82"):
        return "warning"

    severity_map = {
        "E": "error",
        "F": "error",
        "W": "warning",
        "P": "warning",
        "C": "info",  # Convention
        "N": "info",  # Naming
        "Q": "info",  # Quote style
        "T": "warning",  # Type hinting issues
        "R": "info",  # Refactoring suggestions
        "S": "warning",  # Security issues
    }
    return severity_map.get(code[0], "warning")


def transform_ruff_results(lint_errors: List[Dict], cell_line_count: int) -> List[Dict]:
    transformed_messages = []
    for message in lint_errors:
        try:
            code = message.get("code", "")
            severity = get_severity(code)

            # Adjust line numbers for CodeMirror (0-based)
            from_line = max(0, message["location"]["row"] - 1)
            to_line = max(
                0,
                (
                    message["end_location"]["row"] - 1
                    if "end_location" in message
                    else message["location"]["row"] - 1
                ),
            )

            # Ensure line numbers don't exceed the cell's line count
            from_line = min(from_line, cell_line_count - 1)
            to_line = min(to_line, cell_line_count - 1)

            transformed_message = {
                "from": {
                    "line": from_line,
                    "ch": max(0, message["location"]["column"] - 1),
                },
                "to": {
                    "line": to_line,
                    "ch": max(
                        0,
                        (
                            message["end_location"]["column"] - 1
                            if "end_location" in message
                            else message["location"]["column"]
                        ),
                    ),
                },
                "severity": severity,
                "message": f"{message.get('message', 'Error')}",
            }
            transformed_messages.append(transformed_message)
        except KeyError as e:
            logger.error(
                f"Error processing linting message: {str(e)}. Message: {message}"
            )
    return transformed_messages


@async_debounce(0.5)
async def queued_get_cell_linting(
    cell_id: str, text: str, code_w_context: str, websocket: WebSocket
):
    try:
        context_lines = code_w_context.strip().split("\n")
        cell_lines = text.strip().split("\n")

        # More robust way to find the cell start line
        cell_first_line = cell_lines[0].strip()
        cell_start_line = -1

        # Look for the first line of the cell in the context, ignoring whitespace
        for i, line in enumerate(context_lines):
            if line.strip() == cell_first_line:
                # Verify this is actually the start of our cell by checking subsequent lines
                matches = True
                for j, cell_line in enumerate(cell_lines):
                    if (
                        i + j >= len(context_lines)
                        or context_lines[i + j].strip() != cell_line.strip()
                    ):
                        matches = False
                        break
                if matches:
                    cell_start_line = i
                    break

        if cell_start_line == -1:
            # If we can't find the cell in context, just lint the cell directly
            logger.warning(
                f"Could not find cell content in context for cell {cell_id}, linting cell directly"
            )
            lint_errors = await run_ruff_linting(text)
            transformed_messages = transform_ruff_results(lint_errors, len(cell_lines))
            return {cell_id: transformed_messages}

        # Prepare context-aware cell text
        preceding_context = "\n".join(context_lines[:cell_start_line])
        context_aware_cell_text = f"{preceding_context}\n{text}"

        # Run linting on the context-aware cell text
        lint_errors = await run_ruff_linting(context_aware_cell_text)
        logger.debug(f"Ruff output for cell {cell_id}: {json.dumps(lint_errors)}")

        # Filter out linting errors from the preceding context
        preceding_context_line_count = len(preceding_context.split("\n"))
        cell_lint_errors = [
            error
            for error in lint_errors
            if error["location"]["row"] > preceding_context_line_count
        ]

        # Adjust line numbers to be relative to the cell
        for error in cell_lint_errors:
            error["location"]["row"] -= preceding_context_line_count
            if "end_location" in error:
                error["end_location"]["row"] -= preceding_context_line_count

        # Transform results
        transformed_messages = transform_ruff_results(cell_lint_errors, len(cell_lines))

        await websocket.send_json(
            {"cell_id": cell_id, "lint_results": transformed_messages}
        )
    except Exception as e:
        logger.error(
            f"Error processing linting for cell {cell_id}: {str(e)}", exc_info=True
        )