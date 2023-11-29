from fastapi import dependencies
from pydantic import BaseModel, Field
from typing import List, Dict, Union

class CodeRequest(BaseModel):
    id: str
    code: str
    variable_name: str
    cellType: str = Field(enum=['code', 'markdown', 'text', 'sql'])

class Request(BaseModel):
    originId: str
    cells: List[CodeRequest]
    components: Dict[str, Union[str, bool, int, float, List, None]]

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
    originId: str
    components: Dict[str, Union[str, bool, float, int, List, None]]
    userId: str

class DeleteRequest(BaseModel):
    cellId: str

class CreateRequest(BaseModel):
    cellType: str = Field(enum=['code', 'markdown', 'text', 'sql'])
    position_key: str

class SaveRequest(BaseModel):
    id: str
    text: str

class ClearRequest(BaseModel):
    userId: str

class DependencyRequest(BaseModel):
    dependencies: str