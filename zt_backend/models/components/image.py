from pydantic import Field, field_validator
from zt_backend.models.components.zt_component import ZTComponent
import base64

class Image(ZTComponent):
    """Image component for displaying web hosted or local images. Supports .png, .jpg, and .jpeg file types"""
    component: str = Field("v-img", description="Vue component name")
    src: str = Field(..., description="Source URL or Path of the image")
    alt: str = Field("", description="Alternative text for the image")
    width: int = Field(100, description="Width of the image")
    height: int = Field(100, description="Height of the image")

    @field_validator('src')
    def validate_src(cls, src):
        if src.endswith(('.png', ".jpg", ".jpeg")) and not src.startswith('http'):
            try:
                buffer=open(src, 'rb')
                buffer.seek(0)
                b64_img = base64.b64encode(buffer.read()).decode('utf-8')
                if src.endswith((".jpg", ".jpeg")):
                    return f"data:image/jpeg;base64,{b64_img}"
                elif src.endswith(".png"):
                    return f"data:image/png;base64,{b64_img}"
                else:
                    print("Image file type is not supported")
            except Exception as e:
                print("Image not found: ", e)
        return src