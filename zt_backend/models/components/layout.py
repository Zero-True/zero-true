from pydantic import BaseModel,Field
from typing import ForwardRef,Union
from typing import List
from zt_backend.runner.user_state import UserContext

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
        execution_state = UserContext.get_state()
        if execution_state and execution_state.context_globals['exec_mode']:
            execution_state.current_cell_layout.append(self)