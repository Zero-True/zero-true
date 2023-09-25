from pydantic import Field, field_validator, validator
from zt_backend.models.components.zt_component import ZTComponent
from zt_backend.models.state import component_values

class TextArea(ZTComponent):
    """A class for TextInput components inheriting from ZTComponent."""
    component: str = Field("v-textarea", description="Vue component name.")
    value: str = Field ('',description="The input text value")
    placeholder: str = Field(None, description="Placeholder text.")
    label: str = Field(None, description="Label for the text input.")
    readonly: bool = Field(None, description="If true, the input is read-only.")
    disabled: bool = Field(None, description="If true, the input is disabled.")
    triggerEvent: str = Field('input',description="Trigger event to send code to the backend")
    
    @validator('value', always=True) #TODO: debug and replace with field validator
    def get_value_from_global_state(cls, value, values):
        id = values['id'] # Get the id if it exists in the field values
        try:
            if id and id in component_values:  # Check if id exists in global_state
                return component_values[id]  # Return the value associated with id in global_state
        except Exception as e:
            e
        return value  # If id doesn't exist in global_state, return the original value