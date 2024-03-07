from pydantic import Field, validator, field_validator
from zt_backend.models.components.zt_component import ZTComponent
from zt_backend.models.components.validations import validate_color
from typing import List, Optional, Union
from zt_backend.models.state.user_state import UserContext

class Autocomplete(ZTComponent):
    """Autocomplete is a select box that allows users to search the available options. 
    Optimal for when there are many options to choose from"""
    
    component: str = Field("v-autocomplete", description="Vue component name")
    items: List[Union[str, int]] = Field(..., description="Options for the autocomplete box. Can be a list of strings or integers")
    value: Union[str, int, None] = Field("", description="Selected option for the autocomplete box")
    label: Optional[str] = Field(None, description="Label for the autocomplete box")
    multiple: Optional[bool] = Field(None, description="Determines if multiple selections are allowed")
    clearable: Optional[bool] = Field(None, description="Determines if the autocomplete box has a clearable option")
    disabled: Optional[bool] = Field(None, description="Determines if the autocomplete box is disabled")
    readonly: Optional[bool] = Field(None, description="Determines if the autocomplete box is read-only")
    color: Optional[str] = Field(None, pre=True, description="Color of the autocomplete component. Can be custom or standard Material color")
    triggerEvent: str = Field('update:modelValue',description="Trigger event for when to run based on the selected value")

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