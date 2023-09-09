from pydantic import Field, validator
from zt_backend.models.components.zt_component import ZTComponent
from zt_backend.models.validations import validate_color, validate_min_less_than_max

class Slider(ZTComponent):
    """A class for Slider components inheriting from ZTComponent."""
    component: str = Field("SliderComponent", description="Vue component name.")
    value: int = Field(0, description="Current value of the slider.")
    min: int = Field(0, ge=0, description="Minimum value of the slider.")
    max: int = Field(100, ge=0, description="Maximum value of the slider.")
    step: int = Field(1, gt=0, description="Step increment of the slider.")
    thumb_label: bool = Field(None, description="Displays the thumb label.")
    thumb_size: int = Field(None, description="Size of the thumb.")
    tick_labels: bool = Field(None, description="Displays the tick labels.")
    ticks: bool = Field(None, description="Displays the ticks.")
    color: str = Field(None, pre=True, description="Color of the range slider. Can be custom or standard Material color.")
    size: str = Field(None, description="Size of the slider.")
    rounded: bool = Field(None, description="Determines if the slider has rounded edges.")

    @validator('max', allow_reuse=True, pre=True)
    def _validate_max(cls, max_value, values):
        validate_min_less_than_max(max_value, values)

    @validator('color', allow_reuse=True, pre=True)
    def _validate_color(cls, color, values):
        validate_color(color)