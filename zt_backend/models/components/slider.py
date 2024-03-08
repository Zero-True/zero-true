from pydantic import Field, field_validator, validator
from zt_backend.models.components.zt_component import ZTComponent
from zt_backend.models.components.validations import validate_color
from typing import Optional, Union
from zt_backend.models.state.user_state import UserContext

class Slider(ZTComponent):
    """A slider component that allows you to capture numeric input from a user"""
    component: str = Field("v-slider", description="Vue component name")
    value: Union[int,float] = Field(0, description="Current value of the slider")
    min: Union[int,float] = Field(0,  description="Minimum value of the slider")
    max: Union[int,float] = Field(100, description="Maximum value of the slider")
    step: Union[int,float] = Field(1,  description="Step increment of the slider")
    thumb_label: bool = Field(False, description="Displays the thumb label")
    thumb_size: int = Field(0, description="Size of the thumb")
    tick_labels: str = Field('always', description="Displays the tick labels")
    ticks: list = Field([], description="Displays the ticks")
    color: str = Field('primary', pre=True, description="Color of the range slider. Can be custom or standard Material color")
    size: str = Field('large', description="Size of the slider")
    label: Optional[str] = Field(None,description= 'A label for your slider')
    rounded: bool = Field(True, description="Determines if the slider has rounded edges")
    triggerEvent: str = Field('end',description="Trigger event for when to run the slider")
    
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