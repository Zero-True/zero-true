from pydantic import BaseModel, Field
from typing import OrderedDict, List
from zt_backend.models.components.zt_component import ZTComponent

class CodeCell(BaseModel):
    id: str
    code: str
    output: str
    components: List[ZTComponent]
    cellType: str = Field('code', enum=['code', 'markdown'])
    
class Notebook(BaseModel):
    cells: OrderedDict[str, CodeCell]


