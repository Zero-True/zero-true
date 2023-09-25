from pydantic import BaseModel, Field
from typing import List, Dict, Union

class CodeRequest(BaseModel):
    id: str
    code: str
    cellType: str = Field(enum=['code', 'markdown', 'text'])

class Request(BaseModel):
    originId: str
    cells: List[CodeRequest]
    components: Dict[str, Union[str, bool, int,List,None]]

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

class CreateRequest(BaseModel):
    cellType: str = Field(enum=['code', 'markdown', 'text'])