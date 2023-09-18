from pydantic import Field, field_validator
from zt_backend.models.components.zt_component import ZTComponent
from zt_backend.models.validations import validate_color, validate_min_less_than_max
from zt_backend.models.state import component_values

class Slider(ZTComponent):
    """A class for Slider components inheriting from ZTComponent."""
    component: str = Field("v-slider", description="Vue component name.")
    value: int = Field(0, description="Current value of the slider.")
    min: int = Field(0, ge=0, description="Minimum value of the slider.")
    max: int = Field(100, ge=0, description="Maximum value of the slider.")
    step: int = Field(1, gt=0, description="Step increment of the slider.")
    thumb_label: bool = Field(False, description="Displays the thumb label.")
    thumb_size: int = Field(0, description="Size of the thumb.")
    tick_labels: bool = Field(False, description="Displays the tick labels.")
    ticks: list = Field([], description="Displays the ticks.")
    color: str = Field('primary', pre=True, description="Color of the range slider. Can be custom or standard Material color.")
    size: str = Field('large', description="Size of the slider.")
    rounded: bool = Field(True, description="Determines if the slider has rounded edges.")
    
    @field_validator('color')
    def validate_color(cls, color):
        return validate_color(color)
    
    @field_validator('value')
    def get_value_from_global_state(cls, value, values):
        id = values.data['id']  # Get the id if it exists in the field values
        try:
            if id and id in component_values:  # Check if id exists in global_state
                return component_values[id]  # Return the value associated with id in global_state
        except Exception as e:
            e
        return value  # If id doesn't exist in global_state, return the original value