from pydantic import Field
from typing import List
from zt_backend.models.components.zt_component import ZTComponent

class Card(ZTComponent):
    """A class for Card components inheriting from ZTComponent."""
    
    component: str = Field("v-card", description="Vue component name.")
    cardChildren: List[str] = Field([], description="List of child components within the card.")
    color: str = Field(None, description="Background color of the card.")
    elevation: int = Field(None, ge=0, le=24, description="Elevation level of the card. Must be between 0 and 24.")
    density: str = Field(None, enum=['default','comfortable','compact'], description="Density of the component")
    width: int = Field(None, description="Width of the card.")
    location: str = Field(None, enum=['center'])