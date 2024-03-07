from typing import Optional
from pydantic import Field, validator
from zt_backend.models.components.zt_component import ZTComponent
from zt_backend.models.state.user_state import UserContext

class TextArea(ZTComponent):
    """Text area input allows a user to input arbitrary text. This is meant for larger text inputs"""
    component: str = Field("v-textarea", description="Vue component name")
    hint: Optional[str] = Field('Press Enter to Submit', description="Hint text for the text input")
    value: str = Field ('',description="The input text value")
    placeholder: Optional[str] = Field(None, description="Placeholder text")
    label: Optional[str] = Field(None, description="Label for the text input")
    readonly: Optional[bool] = Field(None, description="If true, the input is read-only")
    disabled: Optional[bool] = Field(None, description="If true, the input is disabled")
    triggerEvent: str = Field(None,description="Trigger event to send code to the backend")
    
    @validator('value', always=True) #TODO: debug and replace with field validator
    def get_value_from_global_state(cls, value, values):
        id = values['id'] # Get the id if it exists in the field values
        execution_state = UserContext.get_state()
        try:
            if execution_state and id and id in execution_state.component_values:  # Check if id exists in global_state
                return execution_state.component_values[id]  # Return the value associated with id in global_state
        except Exception as e:
            e
        return value  # If id doesn't exist in global_state, return the original value