from pydantic import BaseModel, Field


class ZTComponent(BaseModel):
    id: str = Field(description="Unique id for a component")
    variable_name: str = Field(None, description="Optional variable name associated with a component")