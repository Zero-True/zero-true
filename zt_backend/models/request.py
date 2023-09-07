from pydantic import BaseModel
from typing import List
import json

class CodeCell(BaseModel):
    code: str

class Request(BaseModel):
    cells: List[CodeCell]