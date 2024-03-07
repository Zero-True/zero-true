from pydantic import BaseModel, Field, field_validator
from zt_backend.models.state.user_state import UserContext

class ZTComponent(BaseModel):
    id: str = Field(description="Unique id for a component")
    variable_name: str = Field('', description="Optional variable name associated with a component")

    def __init__(self, **data):
        super().__init__(**data)
        execution_state = UserContext.get_state()
        if execution_state and execution_state.context_globals['exec_mode']:
            execution_state.current_cell_components.append(self)

    @field_validator('id', mode='before')
    def validate_unique_component_id(cls, id):
        execution_state = UserContext.get_state()
        if execution_state and execution_state.context_globals['exec_mode'] and id in execution_state.created_components:
            raise Exception("Component ID is not unique")
        elif execution_state and execution_state.context_globals['exec_mode']:
            execution_state.created_components.append(id)
            return id
        else:
            return id