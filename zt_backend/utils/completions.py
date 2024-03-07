from copilot.copilot import text_document_did_change
import traceback
import jedi
import logging

logger = logging.getLogger("__name__")

async def get_code_completions(cell_id:str, code: str, line: int, column: int) -> list:

    await text_document_did_change({
        "textDocument": {
            "uri": "file:///notebook.ztnb",
            "version": 1
        },
        "contentChanges": [{
            "text": code
        }]
    })

    code_list = code.split("\n")
    try:
        last_line = code_list[max(line-1,0)]
        if last_line:
            last_char = last_line[max(column-1,0)]
        else:
            last_char = ''
        if last_char in ['.', '(', '[', '{']:
            return {"cell_id": cell_id, "completions": []}

    except Exception as e:
        logger.info("Error formatting completions for cell_id %s: %s", cell_id, traceback.format_exc())

    try:
        script = jedi.Script(code)
        completions = script.complete(line, column)
        completions = [{"label": completion.name, "type": completion.type, "inlineFlag": False} for completion in completions]
        return {"cell_id": cell_id, "completions": completions}
    except Exception:
        logger.debug("Error getting completions for cell_id %s: %s", cell_id, traceback.format_exc())
        return {"cell_id": cell_id, "completions": []}