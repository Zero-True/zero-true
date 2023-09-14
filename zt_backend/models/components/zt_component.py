from pydantic import BaseModel, Field, validator
from zt_backend.models.state import created_components, context_globals

class ZTComponent(BaseModel):
    id: str = Field(description="Unique id for a component")
    variable_name: str = Field('fake', description="Optional variable name associated with a component")

    @validator('id', always=True)
    def validate_unique_component_id(cls, id):
        if context_globals['exec_mode'] and id in created_components:
            raise Exception("Component ID is not unique")
        elif context_globals['exec_mode']:
            created_components.append(id)
            return id
        else:
            return id