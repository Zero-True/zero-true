from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union
from zt_backend.models.notebook import Dependencies
from typing import Literal


class CodeRequest(BaseModel):
    id: str
    code: str
    variable_name: str
    nonReactive: bool
    showTable: bool = Field(False)
    cellType: str = Field(enum=["code", "markdown", "text", "sql"])


class Request(BaseModel):
    originId: str
    reactiveMode: bool = Field(True)
    cells: List[CodeRequest]
    components: Dict[str, Union[str, bool, int, float, List, Dict, None]]


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
    exceptions: Dict[str, str]


class ComponentRequest(BaseModel):
    originId: str
    components: Dict[str, Union[str, bool, float, int, List, Dict, None]]
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
    cellType: str = Field(enum=["code", "markdown", "text", "sql"])
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
    dependencies: Dependencies


class ShareRequest(BaseModel):
    userName: str
    projectName: str
    apiKey: str
    computeProfile: Optional[str] = "xsmall"
    teamName: Optional[str] = ""


class AddCommentRequest(BaseModel):
    cellId: str
    commentId: str
    comment: str
    date: str


class DeleteCommentRequest(BaseModel):
    cellId: str
    commentId: str


class EditCommentRequest(BaseModel):
    cellId: str
    commentId: str
    comment: str


class ResolveCommentRequest(BaseModel):
    cellId: str
    commentId: str
    resolved: bool


class AddReplyRequest(BaseModel):
    cellId: str
    parentCommentId: str
    commentId: str
    comment: str
    date: str


class DeleteReplyRequest(BaseModel):
    cellId: str
    parentCommentId: str
    commentId: str


class EditReplyRequest(BaseModel):
    cellId: str
    parentCommentId: str
    commentId: str
    comment: str


class CreateItemRequest(BaseModel):
    path: str
    name: str
    type: Literal["file", "folder"]


class RenameItemRequest(BaseModel):
    path: str
    oldName: str
    newName: str


class DeleteItemRequest(BaseModel):
    path: str

class FileWrite(BaseModel):
    path: str
    content: str
    chunk_index: int
    total_chunks: int
    
class DownloadRequest(BaseModel):
    path: str
    filename: str
    isFolder: bool