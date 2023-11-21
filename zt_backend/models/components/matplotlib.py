from pydantic import Field
from zt_backend.models.components.zt_component import ZTComponent
import matplotlib.pyplot as plt
import base64
from io import BytesIO

class Matplotlib(ZTComponent):
    component: str = Field("v-img", description="Vue component name.")
    src: str = Field(..., description="Source URL of the image.")
    alt: str = Field("", description="Alternative text for the image.")
    width: int = Field(100, description="Width of the image.")
    height: int = Field(100, description="Height of the image.")
    
    @classmethod
    def from_matplotlib(cls,id: str, figure: plt.Figure, alt=None, width=None, height=None):
        plt.style.use('dark_background')
        buffer = BytesIO()
        figure.savefig(buffer, format="png")
        buffer.seek(0)
        base64_data = base64.b64encode(buffer.read()).decode()
        src = f"data:image/png;base64,{base64_data}"
        return cls(id=id,src=src, alt=alt, width=width, height=height)