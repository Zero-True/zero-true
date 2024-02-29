from typing import Optional
from pydantic import Field
from zt_backend.models.components.zt_component import ZTComponent

class Text(ZTComponent):
    """Text is a read only component that is meant for static text"""
    component: str = Field("v-text", description="Vue component name")
    text: str = Field("", description="The actual text content")
    type: str = Field('text-body-1', enum=[
        'text-h1', 'text-h2', 'text-h3', 'text-h4', 'text-h5', 'text-h6',
        'text-subtitle-1', 'text-subtitle-2', 'text-body-1', 'text-body-2',
        'text-button', 'text-caption', 'text-overline'
    ], description="Text type to display")
    color: Optional[str] = Field(None, description="Color of the text")