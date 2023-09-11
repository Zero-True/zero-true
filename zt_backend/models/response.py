from pydantic import BaseModel, SerializeAsAny
from typing import List
from zt_backend.models.components.zt_component import ZTComponent

class CellResponse(BaseModel):
    id: str
    components: List[SerializeAsAny[ZTComponent]]
    output: str

class Response(BaseModel):
    cells: List[CellResponse]