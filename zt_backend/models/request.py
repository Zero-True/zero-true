from pydantic import BaseModel
from typing import List
from zt_backend.models.components.zt_component import ZTComponent

class CodeCell(BaseModel):
    code: str

class Request(BaseModel):
    cells: List[CodeCell]
    components: List[ZTComponent]