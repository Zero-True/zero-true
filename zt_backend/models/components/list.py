from pydantic import Field
from typing import List, Optional, Union
from zt_backend.models.components.zt_component import ZTComponent

class ListComponent(ZTComponent):
    """A card is a container for components that should be displayed together. 
    Any child components will be placed in their own row within the card and take up the full width"""
    
    component: str = Field("v-list", description="Vue component name")
    childComponents: List[str] = Field([], description="List of child component ids to be placed within the card")
    color: str = Field(None, description="Background color of the card")
    elevation: int = Field(None, ge=0, le=24, description="Elevation level of the card. Must be between 0 and 24")
    density: str = Field(None, enum=['default','comfortable','compact'], description="Density of the component")
    width: Union[int,str] = Field('100%', description="Width of the List")
    height: Union[int,str] = Field('100%', description="Height of the List")

class ListItem(ZTComponent): 
    component: str = Field("v-list-item", description="Vue component name")
    title: str=Field("", description="item title")
    color: str = Field(None, description="Background color of the card")
    elevation: int = Field(None, ge=0, le=24, description="Elevation level of the card. Must be between 0 and 24")
    density: str = Field("default", enum=['default','comfortable','compact'], description="Density of the component")
    width: Union[int,str] = Field('100%', description="Width of the List")
    height: Union[int,str] = Field('100%', description="Height of the List")
    value: str= Field("", description="value for List Item")
    disabled: bool= Field(False, description="removes ability to click List Item")
    childComponents: List[str] = Field([], description="List of child component ids to be placed within the ListItem")


class ListGroup(ZTComponent): 
    component: str = Field("v-list-group", description="Vue component name")
    title: str=Field("", description="item title")
    color: str = Field(None, description="Background color of the card")
    density: str = Field("default", enum=['default','comfortable','compact'], description="Density of the component")
    width: Union[int,str] = Field('100%', description="Width of the List")
    height: Union[int,str] = Field('100%', description="Height of the List")
    value: str= Field("", description="Expands / Collapse the list-group.")
    disabled: bool= Field(False, description="removes ability to click List Item")
    collapse_icon: str= Field("$collapse", description="Icon to display when the list item is expanded.")
    expand_icon: str= Field("$expand", description="Icon to display when the list item is collapsed.")
    childComponents: List[str] = Field([], description="List of child component ids to be placed within the ListGroup")
    ##subgroup:bool= Field(False, description="subgroup for List Group")

class ListItemTitle(ZTComponent): 
    component: str = Field("v-list-item-title", description="Vue component name")
    childComponents: List[str] = Field([], description="List of child component ids to be placed within the ListItemTitle")
    tag: str= Field("div", description="specify a custom tag used on root element")

class ListItemSubtitle(ZTComponent): 
    component: str = Field("v-list-item-subtitle", description="Vue component name")
    childComponents: List[str] = Field([], description="List of child component ids to be placed within the ListItemTitle")
    opacity: Union[int,str]= Field("50%", description="opacity for subtitle")
    tag: str= Field("div", description="specify a custom tag used on root element")

class ListSubheader(ZTComponent): 
    component: str = Field("v-list-subheader", description="Vue component name")
    inset: bool= Field(False, description="inset for Subheader")
    sticky: bool=Field(False,description="sticky for subehader")
    tag: str= Field("div", description="specify a custom tag used on root element")
    title: str=Field("", description="title for subheader")
    childComponents: List[str] = Field([], description="List of child component ids to be placed within the ListComponent")






    

