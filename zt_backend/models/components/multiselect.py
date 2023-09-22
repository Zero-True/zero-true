from pydantic import Field, validator,field_validator
from zt_backend.models.components.zt_component import ZTComponent
from zt_backend.models.validations import validate_color
from typing import List, Union
from zt_backend.models.state import component_values

class MultiSelectBox(ZTComponent):
    """A class for SelectBox components inheriting from ZTComponent."""
    
    component: str = Field("v-combobox", description="Vue component name.")
    
    items: List[Union[str, int]] = Field(..., description="Options for the select box. Can be a list of strings or integers.")
    value: Union[List[Union[str, int,None]],None,str,int] = Field(None, description="Selected option for the select box. Can be a string or integer.")
    label: str = Field(None, description="Label for the select box.")
    multiple: bool = Field(False, description="Determines if multiple selections are allowed.")
    dense: bool = Field(None, description="Determines if the select box is dense.")
    outlined: bool = Field(None, description="Determines if the select box has an outlined style.")
    clearable: bool = Field(None, description="Determines if the select box has a clearable option.")
    disabled: bool = Field(None, description="Determines if the select box is disabled.")
    readonly: bool = Field(None, description="Determines if the select box is read-only.")
    color: str = Field(None, pre=True, description="Color of the range slider. Can be custom or standard Material color.")
    triggerEvent: str = Field('update:modelValue',description="Trigger event for when to run the slider")
    multiple: str = ''
    @field_validator('color')
    def validate_color(cls, color):
        return validate_color(color)

    @validator('value', always=True) #TODO: debug and replace with field validator
    def get_value_from_global_state(cls, value, values):
        id = values['id'] # Get the id if it exists in the field values
        try:
            if id and id in component_values:  # Check if id exists in global_state
                return component_values[id]  # Return the value associated with id in global_state
        except Exception as e:
            e
        return value  # If id doesn't exist in global_state, return the original value