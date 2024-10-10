from copilot.copilot import text_document_did_change
import traceback
import jedi
import logging
from typing import List, Dict, Any
import re


logger = logging.getLogger("__name__")

async def get_code_completions(cell_id: str, code: str, line: int, column: int) -> list:
     
    await text_document_did_change({
        "textDocument": {
            "uri": "file:///notebook.ztnb",
            "version": 1
        },
        "contentChanges": [{
            "text": code
        }]
    })
    code_lines = code.split("\n")

    try:
       
        if line > len(code_lines) or should_skip_completions(code_lines, line - 1, column - 1):
            return {"cell_id": cell_id, "completions": []}

        script = jedi.Script(code)
        completions = script.complete(line, column)
        
        sorted_completions = filter_and_sort_completions(completions, code_lines[line - 1], column - 1)
        
        return {"cell_id": cell_id, "completions": sorted_completions}
    except Exception:
        logger.debug(f"Error getting completions for cell_id {cell_id}")
        return {"cell_id": cell_id, "completions": []}

def should_skip_completions(code_lines: List[str], line_index: int, cursor_position: int) -> bool:
    if line_index >= len(code_lines):
        return True

    current_line = code_lines[line_index]

    if not current_line or cursor_position > len(current_line):
        return True

    if '#' in current_line[:cursor_position]:
        return True

    stripped_line = current_line.strip()
    line_starters = ('class', 'def', 'if', 'elif', 'else:', 'while', 'for', 'try:', 
                     'except', 'finally:', 'with', 'import', 'from', 'return', 'break', 
                     'continue', 'pass')
    
    return any(stripped_line.startswith(starter) for starter in line_starters)

def filter_and_sort_completions(completions: List[Any], line: str, column: int) -> List[Dict[str, Any]]:
    if column == 0:
        return []
        
    last_char = line[column]
    
    if last_char.isalnum() or last_char == '_':
        current_word = re.findall(r'\w+$', line[:column+1])
        current_word = current_word[0] if current_word else ''
        
        filtered_completions = [
            {
                "label": c.name,
                "type": c.type,
                "inlineFlag": False
            }
            for c in completions
            if c.name.lower().startswith(current_word.lower()) and not c.name.startswith('_')
        ]
        
        return sorted(filtered_completions, 
                      key=lambda x: (not x['label'].lower().startswith(current_word.lower()),
                                     not x['label'].startswith(current_word),
                                     x['label'].lower()))
    return []
