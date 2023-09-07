from pydantic import BaseModel
from typing import List
import json

class CodeCell(BaseModel):
    code: str

class Request(BaseModel):
    cells: List[CodeCell]

with open('test.json', 'w+') as file:
    json.dump(Request.model_json_schema(), file)