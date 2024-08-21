from typing import Union
from pydantic import Field, validator
from zt_backend.models.components.zt_component import ZTComponent
from zt_backend.models.state.user_state import UserContext


class iFrame(ZTComponent):
    """This is a representation of a standard iframe component"""

    component: str = Field("iframe", description="Vue component name")
    src: str = Field("", description="Source URL of the iframe")
    width: Union[int, str] = Field("100%", description="Width of the iframe")
    height: Union[int, str] = Field("100%", description="Height of the iframe")
    frameborder: int = Field(0, description="Frame border of the iframe")
    scrolling: str = Field("auto", description="Scrolling of the iframe")
    allowtransparency: bool = Field(
        False, description="Allow transparency of the iframe"
    )
