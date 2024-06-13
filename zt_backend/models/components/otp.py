from typing import List, Optional,Union
from pydantic import Field, field_validator, validator
from zt_backend.models.components.zt_component import ZTComponent
from zt_backend.models.components.validations import validate_color
from zt_backend.models.state.user_state import UserContext

class Otp(ZTComponent):
    """A Otp component that allows for passwords or authentication"""
    component: str = Field("v-otp", description="Vue component name")
    value: Union[str,int] = Field ('', description="The input text value")
    autofocus: bool = Field(False, description="Vue component name")
    disabled: bool = Field(False, description="If true, the input is disabled")
    color: str = Field('primary', pre=True, description="Color of the switch. Can be custom or standard Material color")
    divider: bool = Field(False, description='Divider for otp')
    width: Union[int,str] = Field('100%', description="Width of the switch")
    type: str= Field("number",description="Type of otp")

    triggerEvent: str = Field('finish', description="Trigger event for when to trigger a run")
    loading: bool =Field(False,description="Loading for otp")
    
    @field_validator('color')
    def validate_color(cls, color):
        return validate_color(color)
    
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
    