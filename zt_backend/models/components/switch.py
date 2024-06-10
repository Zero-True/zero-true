from typing import List, Optional,Union
from pydantic import Field, field_validator, validator
from zt_backend.models.components.zt_component import ZTComponent
from zt_backend.models.components.validations import validate_color
from zt_backend.models.state.user_state import UserContext

class Switch(ZTComponent):
    """A slider component that allows a user to select a range of values"""
    component: str = Field("v-switch", description="Vue component name")
    value: str = Field ('', description="The input text value")
    hint: Optional[str] = Field('', description="Hint text for switch")
    disabled: Optional[bool] = Field(None, description="If true, the input is disabled")
    color: str = Field('primary', pre=True, description="Color of the switch. Can be custom or standard Material color")
    label: Optional[str] = Field(None,description= 'A label for your switch')
    multiple: Optional[bool] = Field(None, description="Determines if multiple selections are allowed")
    width: Union[int,str] = Field('100%', description="Width of the switch")
    triggerEvent: str = Field('update:modelValue',description="Trigger event for when to trigger a run")
    readonly: Optional[bool] = Field(None, description="Determines if the Switch is read-only")
    
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
    
