from pydantic import Field, validator, field_validator
from zt_backend.models.components.zt_component import ZTComponent
from zt_backend.models.validations import validate_color
from typing import List, Union, Optional
from zt_backend.runner.user_state import UserContext

class MultiSelectBox(ZTComponent):
    """A class for SelectBox components inheriting from ZTComponent."""
    
    component: str = Field("v-combobox", description="Vue component name.")
    
    items: List[Union[str, int]] = Field(..., description="Options for the select box. Can be a list of strings or integers.")
    value: Union[List[Union[str, int,None]],None,str,int] = Field(None, description="Selected option for the select box. Can be a string or integer.")
    label: Optional[str] = Field(None, description="Label for the select box.")
    multiple: Optional[bool] = Field(None, description="Determines if multiple selections are allowed.")
    dense: Optional[bool] = Field(None, description="Determines if the select box is dense.")
    outlined: Optional[bool] = Field(None, description="Determines if the select box has an outlined style.")
    clearable: Optional[bool] = Field(None, description="Determines if the select box has a clearable option.")
    disabled: Optional[bool] = Field(None, description="Determines if the select box is disabled.")
    readonly: Optional[bool] = Field(None, description="Determines if the select box is read-only.")
    color: Optional[str] = Field(None, pre=True, description="Color of the range slider. Can be custom or standard Material color.")
    triggerEvent: str = Field('update:modelValue',description="Trigger event for when to run the slider")
    multiple: str = ''
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