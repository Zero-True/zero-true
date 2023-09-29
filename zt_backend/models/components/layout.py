from pydantic import BaseModel,Field
from zt_backend.models.state import current_cell_layout,context_globals


from typing import List

class ZTColumn(BaseModel):
    id: str = Field(..., description="Unique id for a column")
    components: List[str] = Field([], description="List of component IDs that belong to this column")

class ZTRow(BaseModel):
    id: str = Field(..., description="Unique id for a row")
    columns: List[ZTColumn] = Field([], description="List of columns that belong to this row")

class ZTLayout(BaseModel):
    rows: List[ZTRow] = Field([], description="List of rows that make up this layout")

    def __init__(self, **data):
        super().__init__(**data)
        if context_globals['exec_mode']:
            current_cell_layout.append(self)
