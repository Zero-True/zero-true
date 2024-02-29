from pydantic import Field
from typing import List, Optional
from zt_backend.models.components.zt_component import ZTComponent

class Card(ZTComponent):
    """A card is a container for components that should be displayed together. 
    Any child components will be placed in their own row within the card and take up the full width"""
    
    component: str = Field("v-card", description="Vue component name")
    cardChildren: List[str] = Field([], description="List of child component ids to be placed within the card")
    color: Optional[str] = Field(None, description="Background color of the card")
    elevation: Optional[int] = Field(None, ge=0, le=24, description="Elevation level of the card. Must be between 0 and 24")
    density: Optional[str] = Field(None, enum=['default','comfortable','compact'], description="Density of the component")
    width: Optional[int] = Field(None, description="Width of the card")
    location: Optional[str] = Field(None, enum=['center'])