from pydantic import BaseModel, Field, field_validator
from zt_backend.models.state import created_components, context_globals, current_cell_components

class ZTComponent(BaseModel):
    id: str = Field(description="Unique id for a component")
    variable_name: str = Field('', description="Optional variable name associated with a component")


    def __init__(self, **data):
        super().__init__(**data)
        if context_globals['exec_mode']:
            current_cell_components.append(self)

    @field_validator('id', mode='before')
    def validate_unique_component_id(cls, id):
        if context_globals['exec_mode'] and id in created_components:
            raise Exception("Component ID is not unique")
        elif context_globals['exec_mode']:
            created_components.append(id)
            return id
        else:
            return id