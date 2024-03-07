from pydantic import BaseModel,Field
from typing import ForwardRef,Union
from typing import List
from zt_backend.models.state.user_state import UserContext

Row = ForwardRef('Row')
Column = ForwardRef('Column')

class Column(BaseModel):
    """A Column must be a subcomponent of a Row. It can contain both individual components and rows"""
    components: List[Union[str,"Row"]] = Field([], description="List of component IDs and rows that belong to this column, rendered in order")
    width: Union[int,bool] = Field(False, description="Width of the column. It can be a number 1-12 and by default is automatically calculated")

    def __init__(__pydantic_self__, *args, **data):
        if args:
            data['components'] = args[0]
            if len(args) > 1:
                data['width'] = args[1]
        super().__init__(**data)
    
class Row(BaseModel):
    """Rows can contain both individual components and columns. They are the top level components of a layout and can be subcomponents of columns"""
    components: List[Union[str,Column]] = Field([], description="List of component IDs and columns that belong to this row, rendered in order")

    def __init__(self, *args, **data):
        if args:
            data['components'] = args[0]
        super().__init__(**data)

class Layout(BaseModel):
    """Layout is an object that contains the list of rows to be rendered"""
    rows: List[Row] = Field([], description="List of rows in this layout")

    def __init__(self, *args, **data):
        if args:
            data['rows'] = args[0]
        super().__init__(**data)
        execution_state = UserContext.get_state()
        if execution_state and execution_state.context_globals['exec_mode']:
            execution_state.current_cell_layout.append(self)