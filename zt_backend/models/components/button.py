from pydantic import Field, validator
from zt_backend.models.components.zt_component import ZTComponent
from zt_backend.models.state.user_state import UserContext

class Button(ZTComponent):
    """Standard button UI component"""
    component: str = Field("v-btn", description="Vue component name")
    value: bool = Field (False, description="Whether the button has been clicked")
    text: str = Field("Click Me", description="Label displayed on the button")
    color: str = Field("primary", description="Color of the button")
    disabled: bool = Field(False, description="If true, the button is disabled")
    outlined: bool = Field(False, description="If true, the button will have an outlined style")
    triggerEvent: str = Field("click", description="Trigger event to send code to the backend")

    @validator('value', always=True)
    def get_label_from_global_state(cls, value, values):
        id = values.get('id')  # Get the id if it exists in the field values
        execution_state = UserContext.get_state()
        try:
            if execution_state and id and id in execution_state.component_values:  # Check if id exists in global_state
                return execution_state.component_values[id]  # Return the value associated with id in global_state
        except Exception as e:
            pass  # Handle exception as needed
        return (value)  # If id doesn't exist in global_state, return the original value
