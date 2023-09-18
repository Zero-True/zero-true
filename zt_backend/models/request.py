from pydantic import BaseModel
from typing import List, Dict, Union, Optional

class CodeRequest(BaseModel):
    id: str
    code: str

class Request(BaseModel):
    originId: Optional(str)
    cells: List[CodeRequest]
    components: Dict[str, Union[str, bool, int]]

class Cell(BaseModel):
    code: str
    defined_names: List[str]
    loaded_names: List[str]
    child_cells: List[int] = []
    parent_cells: List[int] = []
    previous_child_cells: List[int] = []

class CodeDict(BaseModel):
    cells: Dict[str, Cell]

class ComponentRequest(BaseModel):
    componentId: str
    componentValue: Union[str, bool, int]

class DeleteRequest(BaseModel):
    cellId: str
