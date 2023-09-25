from pydantic import Field
from zt_backend.models.components.zt_component import ZTComponent

class Image(ZTComponent):
    """A class for Image components inheriting from ZTComponent."""
    component: str = Field("v-img", description="Vue component name.")
    src: str = Field(..., description="Source URL of the image.")
    alt: str = Field(None, description="Alternative text for the image.")
    width: int = Field(None, description="Width of the image.")
    height: int = Field(None, description="Height of the image.")