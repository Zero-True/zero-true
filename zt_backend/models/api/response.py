from pydantic import BaseModel, SerializeAsAny, Field
from typing import List
from zt_backend.models.components.zt_component import ZTComponent
from zt_backend.models.components.layout import Layout
from typing import Union


class CellResponse(BaseModel):
    id: str
    components: List[SerializeAsAny[ZTComponent]]
    layout: Union[Layout,None]
    output: str

class Response(BaseModel):
    cells: List[CellResponse]
    refresh: bool = Field(False)