from pydantic import Field, field_validator, validator
from zt_backend.models.components.zt_component import ZTComponent
from zt_backend.models.components.validations import validate_color
from typing import Optional, Union
from zt_backend.models.state.user_state import UserContext

class Rating(ZTComponent):
    """A rating component that allows you to capture user ratings"""
    component: str = Field("v-rating", description="Vue component name")
    value: Union[int, float] = Field(0, description="Current rating value")
    max: Union[int, float] = Field(5, description="Maximum rating value")
    size: str = Field('medium', description="Size of the rating component")
    color: str = Field('primary', pre=True, description="Color of the rating component. Can be custom or standard Material color")
    readonly: bool = Field(False, description="Determines if the rating component is readonly")
    label: Optional[str] = Field(None, description="A label for your rating component")
    triggerEvent: str = Field('update:modelValue', description="Trigger event for when to run the rating")

    @field_validator('color')
    def validate_color(cls, color):
        return validate_color(color)

    @validator('value', always=True) #TODO: debug and replace with field validator
    def get_value_from_global_state(cls, value, values):
        id = values.get('id')  # Get the id if it exists in the field values
        execution_state = UserContext.get_state()
        try:
            if execution_state and id and id in execution_state.component_values:  # Check if id exists in global_state
                return execution_state.component_values[id]  # Return the value associated with id in global_state
        except Exception as e:
            print(f"Error retrieving value from global state: {e}")
        return value  # If id doesn't exist in global_state, return the original value
