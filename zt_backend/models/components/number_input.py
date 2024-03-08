from pydantic import Field, validator
from zt_backend.models.components.zt_component import ZTComponent
from typing import Union,Optional
from zt_backend.models.state.user_state import UserContext

class NumberInput(ZTComponent):
    """Number input allows a user to input an arbitrary number. Can be a float or an integer"""
    component: str = Field("v-number-field", description="Vue component name")
    hint: Optional[str] = Field('Press Enter to Submit', description="Hint text for the number input")
    value: Union[int,float,None] = Field (None,description="The input number value")
    placeholder: Optional[Union[int,float]] = Field(None, description="Placeholder number")
    label: Optional[str] = Field(None, description="Label for the number input")
    readonly: Optional[bool] = Field(None, description="If true, the input is read-only")
    disabled: Optional[bool] = Field(None, description="If true, the input is disabled")
    type: str = Field('number',description="Ensures that only numbers are accepted on the frontend")
    triggerEvent: str = Field(None,description="Trigger event to send code to the backend")
    
    @validator('value', always=True) #TODO: debug and replace with field validator
    def get_value_from_global_state(cls, value, values):
        if value=="":
            return None
        id = values['id'] # Get the id if it exists in the field values
        execution_state = UserContext.get_state()
        try:
            if execution_state and id and id in execution_state.component_values:  # Check if id exists in global_state
                return execution_state.component_values[id]  # Return the value associated with id in global_state
        except Exception as e:
            e
        return value  # If id doesn't exist in global_state, return the original value