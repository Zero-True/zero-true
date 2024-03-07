from pydantic import BaseModel, Field
from typing import List, Dict, Union

class CodeRequest(BaseModel):
    id: str
    code: str
    variable_name: str
    nonReactive: bool
    showTable: bool = Field(False)
    cellType: str = Field(enum=['code', 'markdown', 'text', 'sql'])

class Request(BaseModel):
    originId: str
    cells: List[CodeRequest]
    components: Dict[str, Union[str, bool, int, float, List, None]]

class Cell(BaseModel):
    code: str
    nonReactive: bool
    defined_names: List[str]
    loaded_names: List[str]
    loaded_modules: List[str] = []
    imported_modules: List[str] = []
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

class NotebookNameRequest(BaseModel):
    notebookName: str

class HideCellRequest(BaseModel):
    cellId: str
    hideCell: bool

class HideCodeRequest(BaseModel):
    cellId: str
    hideCode: bool

class NameCellRequest(BaseModel):
    cellId: str
    cellName: str

class CellReactivityRequest(BaseModel):
    cellId: str
    nonReactive: bool

class ExpandCodeRequest(BaseModel):
    cellId: str
    expandCode: bool

class ShowTableRequest(BaseModel):
    cellId: str
    showTable: bool

class CreateRequest(BaseModel):
    cellType: str = Field(enum=['code', 'markdown', 'text', 'sql'])
    position_key: str

class SaveRequest(BaseModel):
    id: str
    text: str
    code_w_context: str = Field("")
    cellType: str
    line: str = Field("")
    column: str = Field("")

class ClearRequest(BaseModel):
    userId: str

class DependencyRequest(BaseModel):
    dependencies: str

class ShareRequest(BaseModel):
    userName: str
    projectName: str
    apiKey: str
    