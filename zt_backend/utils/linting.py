import asyncio
from typing import List, Dict, Union, Callable, Coroutine, Any
import tempfile
import os
import json
import logging
from fastapi import HTTPException


logger = logging.getLogger(__name__)

class LintingQueue:
    def __init__(self, interval: float):
        self.interval = interval
        self.queue: asyncio.Queue = asyncio.Queue()
        self.processing_task: asyncio.Task = asyncio.create_task(self._process_queue())

    async def enqueue(self, coro: Callable[..., Coroutine[Any, Any, Any]], *args, **kwargs):
        future = asyncio.Future()
        await self.queue.put((coro, args, kwargs, future))
        return await future

    async def _process_queue(self):
        while True:
            await asyncio.sleep(self.interval)
            if not self.queue.empty():
                coro, args, kwargs, future = await self.queue.get()
                try:
                    # Process only the most recent request
                    while not self.queue.empty():
                        coro, args, kwargs, future = self.queue.get_nowait()
                    result = await coro(*args, **kwargs)
                    future.set_result(result)
                except Exception as e:
                    future.set_exception(e)

linting_queue = LintingQueue(interval=1.0)  # Process queue every 1 second

async def queued_get_cell_linting(cell_id: str, cell_code: str, context_code: str):
    """
    Queued version of get_cell_linting
    """
    return await linting_queue.enqueue(get_cell_linting, cell_id, cell_code, context_code)

async def get_cell_linting(cell_id: str, cell_code: str, context_code: str) -> Dict[str, List[Dict[str, Union[int, str, Dict[str, int]]]]]:
    """
    Lint the provided Python code for a specific cell, considering the context, and return the linting results.
    """
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(context_code)
            temp_file_path = temp_file.name

        # Run pylint as a subprocess
        process = await asyncio.create_subprocess_exec(
            'pylint', temp_file_path, '--output-format=json',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        os.unlink(temp_file_path)

        if stderr:
            logger.error(f"Pylint error: {stderr.decode()}")
            raise HTTPException(status_code=500, detail=f"Pylint error: {stderr.decode()}")

        if not stdout:
            return {cell_id: []}

        lint_messages = json.loads(stdout.decode())
        
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
    """
    severity_map = {
        "convention": "info",
        "refactor": "info",
        "warning": "warning",
        "error": "error",
        "fatal": "error"
    }
    return severity_map.get(pylint_type.lower(), "info")