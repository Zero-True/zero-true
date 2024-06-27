from pydantic import Field, validator, field_validator
from typing import List, Optional, Union
from zt_backend.models.components.zt_component import ZTComponent
from zt_backend.models.components.validations import validate_color


class ListComponent(ZTComponent):
    """List the Primary components holding the items in the scorllable format"""

    component: str = Field("v-list", description="Vue component name for List")
    childComponents: List[str] = Field(
        [], description="List of child component ids to be placed within the List"
    )

    color: str = Field("primary", description="Background color of the List")
    elevation: int = Field(
        None,
        ge=0,
        le=24,
        description="Elevation level of the List. Must be between 0 and 24",
    )
    density: str = Field(
        None,
        enum=["default", "comfortable", "compact"],
        description="Density of the List",
    )
    width: Union[int, str] = Field("100%", description="Width of the List")
    height: Union[int, str] = Field("100%", description="Height of the List")

    @field_validator("color")
    def validate_color(cls, color):
        return validate_color(color)


class ListItem(ZTComponent):
    """List Item helps define properties of individual items in the list"""

    component: str = Field(
        "v-list-item", description="Vue component name for List Item"
    )
    title: str = Field("", description="item title")
    color: str = Field("primary", description="Background color of the List item")
    elevation: int = Field(
        None,
        ge=0,
        le=24,
        description="Elevation level of the List item. Must be between 0 and 24",
    )
    density: str = Field(
        "default",
        enum=["default", "comfortable", "compact"],
        description="Density of the List Item: default | comfortable | compact",
    )
    width: Union[int, str] = Field("100%", description="Width of the List item")
    height: Union[int, str] = Field("100%", description="Height of the List item")
    value: str = Field("", description="value for List Item")
    disabled: bool = Field(False, description="removes ability to click List Item")
    childComponents: List[str] = Field(
        [],
        description="List of child component ids to be placed within the ListItem. List title, subtitle come as the child components of the list item",
    )

    @field_validator("color")
    def validate_color(cls, color):
        return validate_color(color)

class ListItemTitle(ZTComponent):
    """List Item Title is used to specify the title of the Lsit Item. Use Text component to provide the title details and pass it to the child component of List Item."""

    component: str = Field(
        "v-list-item-title", description="Vue component name for List item title"
    )
    childComponents: List[str] = Field(
        [],
        description="List of child component ids to be placed within the ListItemTitle. Mention v-test component to show the text of title",
    )


class ListItemSubtitle(ZTComponent):
    """List Item SubtitleTitle is used to specify the Subtitle of the List Item. Use Text component to provide the text details of the subtitle and pass it to the child component of List Item"""

    component: str = Field(
        "v-list-item-subtitle", description="Vue component name for List Item Subtitle"
    )
    childComponents: List[str] = Field(
        [],
        description="List of child component ids to be placed within the ListItemTitle. Mention v-test component to show the text of Subtitle",
    )

class ListSubheader(ZTComponent):
    """List SubHeader is used to specify the Sub Header of the List. Use Text component to provide the title details and pass it to the child component of List."""

    component: str = Field(
        "v-list-subheader", description="Vue component name for List SubHeader "
    )
    inset: bool = Field(False, description="inset for Subheader")
    sticky: bool = Field(False, description="sticky for subehader")
    childComponents: List[str] = Field(
        [],
        description="List of child component ids to be placed within the List Subheader. Mention v-text component to show title for subheader",
    )
  
