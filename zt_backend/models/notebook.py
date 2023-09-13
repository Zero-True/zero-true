from pydantic import BaseModel, Field, SerializeAsAny
from typing import OrderedDict, List
from zt_backend.models.components.zt_component import ZTComponent

class CodeCell(BaseModel):
    id: str
    code: str
    output: str
    components: List[SerializeAsAny[ZTComponent]]
    cellType: str = Field('code', enum=['code', 'markdown'])
    
class Notebook(BaseModel):
    cells: OrderedDict[str, CodeCell]


