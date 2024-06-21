from pydantic import Field
from typing import List, Optional, Union
from zt_backend.models.components.zt_component import ZTComponent

class ListComponent(ZTComponent):
    """List the Primary components holding the items in the scorllable format"""
    component: str = Field("v-list", description="Vue component name for List")
    childComponents: List[str] = Field([], description="List of child component ids to be placed within the List")
    color: str = Field(None, description="Background color of the List")
    elevation: int = Field(None, ge=0, le=24, description="Elevation level of the List. Must be between 0 and 24")
    density: str = Field(None, enum=['default','comfortable','compact'], description="Density of the List")
    width: Union[int,str] = Field('100%', description="Width of the List")
    height: Union[int,str] = Field('100%', description="Height of the List")

class ListItem(ZTComponent): 
    """List Item helps define properties of individual items in the list"""
    component: str = Field("v-list-item", description="Vue component name for List Item")
    title: str=Field("", description="item title")
    color: str = Field(None, description="Background color of the List item")
    elevation: int = Field(None, ge=0, le=24, description="Elevation level of the List item. Must be between 0 and 24")
    density: str = Field("default", enum=['default','comfortable','compact'], description="Density of the List Item: default | comfortable | compact")
    width: Union[int,str] = Field('100%', description="Width of the List item")
    height: Union[int,str] = Field('100%', description="Height of the List item")
    value: str= Field("", description="value for List Item")
    disabled: bool= Field(False, description="removes ability to click List Item")
    childComponents: List[str] = Field([], description="List of child component ids to be placed within the ListItem. List title, subtitle come as the child components of the list item")


class ListGroup(ZTComponent): 
    """List Group is used to group multiple list items in one category"""
    component: str = Field("v-list-group", description="Vue component name for List group")
    title: str=Field("", description="Title of the List Group")
    color: str = Field(None, description="Background color of the List Group")
    density: str = Field("default", enum=['default','comfortable','compact'], description="Density of the component")
    width: Union[int,str] = Field('100%', description="Width of the List")
    height: Union[int,str] = Field('100%', description="Height of the List")
    value: str= Field("", description="Expands / Collapse the list-group.")
    disabled: bool= Field(False, description="removes ability to click List Item")
    collapse_icon: str= Field("$collapse", description="Icon to display when the list item is expanded.")
    expand_icon: str= Field("$expand", description="Icon to display when the list item is collapsed.")
    childComponents: List[str] = Field([], description="List of child component ids to be placed within the ListGroup. List Items come as child Components of the Group")
    ##subgroup:bool= Field(False, description="subgroup for List Group")

class ListItemTitle(ZTComponent): 
    """List Item Title is used to specify the title of the Lsit Item. Use Text component to provide the title details and pass it to the child component of List Item."""
    component: str = Field("v-list-item-title", description="Vue component name for List item title")
    childComponents: List[str] = Field([], description="List of child component ids to be placed within the ListItemTitle. Mention v-test component to show the text of title")
    tag: str= Field("div", description="specify a custom tag used on root element")

class ListItemSubtitle(ZTComponent): 
    """List Item SubtitleTitle is used to specify the Subtitle of the List Item. Use Text component to provide the text details of the subtitle and pass it to the child component of List Item"""
    component: str = Field("v-list-item-subtitle", description="Vue component name for List Item Subtitle")
    childComponents: List[str] = Field([], description="List of child component ids to be placed within the ListItemTitle. Mention v-test component to show the text of Subtitle")
    opacity: Union[int,str]= Field("50%", description="opacity for subtitle")
    tag: str= Field("div", description="specify a custom tag used on root element")

class ListSubheader(ZTComponent): 
    """List SubHeader is used to specify the Sub Header of the List. Use Text component to provide the title details and pass it to the child component of List."""
    component: str = Field("v-list-subheader", description="Vue component name for List SubHeader ")
    inset: bool= Field(False, description="inset for Subheader")
    sticky: bool=Field(False,description="sticky for subehader")
    tag: str= Field("div", description="specify a custom tag used on root element")
    title: str=Field("", description="title for subheader")
    childComponents: List[str] = Field([], description="List of child component ids to be placed within the List Subheader. Mention v-text component to show title for subheader")