from pydantic import Field, field_validator
from typing import List, Optional, Union
from zt_backend.models.components.zt_component import ZTComponent
from zt_backend.models.components.validations import validate_color


class ExpansionPanels(ZTComponent):
    """
    A group of expansion panels where the title is shown and the desciption can be hidden or expanded to view.
    It is useful for reducing vertical space with large amounts of information
    """

    component: str = Field("v-expansion-panels", description="Vue component name")
    childComponents: List[str] = Field(
        [],
        description="List of child component ids to be placed within the panels group",
    )
    value: Union[List[Union[int, None]], None, int] = Field(
        [], description="Values of the panels selected to expand indexed at 0"
    )
    multiple: bool = Field(
        False, description="Determines if multiple expansions are allowed"
    )
    color: str = Field("primary", description="Background color of the panel")
    disabled: bool = Field(
        False, description="Determines if the expansion panels are disabled"
    )
    readonly: bool = Field(
        False, description="Determines if the expansion panels are read-only"
    )

    @field_validator("color")
    def validate_color(cls, color):
        return validate_color(color)


class ExpansionPanel(ZTComponent):
    """Expansion Panel component"""

    component: str = Field("v-expansion-panel", description="Vue component name")
    childComponents: List[str] = Field(
        [], description="List of child component ids to be placed within the panel"
    )
    title: Optional[str] = Field("", description="Specify a title text for the panel")
    text: Optional[str] = Field("", description="Specify content text for the panel")
    color: str = Field("primary", description="Background color of the expansion panel")
    disabled: bool = Field(
        False, description="Determines if the expansion panel is disabled"
    )
    readonly: bool = Field(
        False, description="Determines if the expansion panel is read-only"
    )

    @field_validator("color")
    def validate_color(cls, color):
        return validate_color(color)


class ExpansionPanelTitle(ZTComponent):
    """Expansion Panel Title component is used to modify the features of Expansion Panel's title. Wraps the #title slot"""

    component: str = Field(
        "v-expansion-title", description="Vue component name for expansion panel title"
    )
    childComponents: List[str] = Field(
        [],
        description="List of child component ids to be placed within the title. This could be a v-text component",
    )
    color: str = Field("primary", description="Background color of the expansion panel")
    readonly: bool = Field(
        False, description="Determines if the expansion panels is read-only"
    )

    @field_validator("color")
    def validate_color(cls, color):
        return validate_color(color)


class ExpansionPanelText(ZTComponent):
    """Expansion Panel Text component is used to modify the features of Expansion Panel's text. Wraps the #text slot"""

    component: str = Field(
        "v-expansion-panel-text",
        description="Vue component name for expansion panels text",
    )
    childComponents: List[str] = Field(
        [],
        description="List of child component ids to be placed within the Text. This could be a v-text component",
    )
