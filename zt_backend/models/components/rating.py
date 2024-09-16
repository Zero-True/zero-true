from pydantic import Field, field_validator, validator
from zt_backend.models.components.zt_component import ZTComponent
from zt_backend.models.components.validations import validate_color
from typing import Optional, Union, List
from zt_backend.models.state.user_state import UserContext


class Rating(ZTComponent):
    """A rating component that allows you to capture star-based input from a user"""

    component: str = Field("v-rating", description="Vue component name")
    value: Union[str, float] = Field(0, description="Current value of the rating")
    length: Union[str, int] = Field(5, description="Number of rating icons")
    hover: bool = Field(
        True, description="Provides visual feedback when hovering over icons"
    )
    size: Union[str, int] = Field("default", description="Size of the rating icons")
    color: Optional[str] = Field(
        "primary", description="Color of the rating icons when active"
    )
    active_color: Optional[str] = Field(
        "primary",
        description="The applied color when the component is in an active state",
    )
    half_increments: bool = Field(
        False, description="Allows for half-increment ratings"
    )
    readonly: bool = Field(
        False, description="Removes all hover effects and pointer events"
    )
    density: str = Field(
        "default", description="Adjusts the vertical height used by the component"
    )
    disabled: bool = Field(
        False, description="Removes the ability to click or target the component"
    )
    item_aria_label: str = Field(
        "$vuetify.rating.ariaLabel.item", description="Aria label for each item"
    )
    item_label_position: str = Field("top", description="Position of item labels")
    item_labels: Optional[List[str]] = Field(
        None, description="Array of labels to display next to each item"
    )
    ripple: bool = Field(False, description="Applies the v-ripple directive")
    triggerEvent: str = Field(
        "update:modelValue", description="Trigger event for when to run the rating"
    )

    @field_validator("color", "active_color")
    def validate_color(cls, color):
        return validate_color(color)

    @field_validator("density")
    def validate_density(cls, v):
        if v not in ["default", "comfortable", "compact"]:
            raise ValueError(
                "Density must be one of 'default', 'comfortable', or 'compact'"
            )
        return v

    @field_validator("item_label_position")
    def validate_item_label_position(cls, v):
        if v not in ["top", "bottom"]:
            raise ValueError("Item label position must be either 'top' or 'bottom'")
        return v

    @validator("value", always=True)
    def get_value_from_global_state(cls, value, values):
        id = values.get("id")
        execution_state = UserContext.get_state()
        try:
            if execution_state and id and id in execution_state.component_values:
                return execution_state.component_values[id]
        except Exception as e:
            pass
        return value
