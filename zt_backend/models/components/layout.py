from pydantic import BaseModel,Field
from typing import ForwardRef,Union
from zt_backend.models.state import current_cell_layout,context_globals
from typing import List

Row = ForwardRef('Row')
Column = ForwardRef('Column')

class Column(BaseModel):
    components: List[Union[str,"Row"]] = Field([], description="List of component IDs that belong to this column")
    width: Union[int,bool] = Field(False)
    

class Row(BaseModel):
    components: List[Union[str,Column]] = Field([], description="List of columns that belong to this row")


class Layout(BaseModel):
    rows: List[Row] = Field([], description="List of rows in this layout")
    columns: List[Column] = Field([], description="List of columns in this layout")

    def __init__(self, **data):
        super().__init__(**data)
        if context_globals['exec_mode']:
            current_cell_layout.append(self)