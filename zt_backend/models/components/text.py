from pydantic import Field
from zt_backend.models.components.zt_component import ZTComponent
from zt_backend.models.state import component_values



class Text(ZTComponent):
    """A class for static text components inheriting from ZTComponent."""
    component: str = Field("v-text", description="Vue component name for static text.")
    text: str = Field("", description="The actual text content.")
    text_type: str = Field('text-body-1', enum=[
        'text-h1', 'text-h2', 'text-h3', 'text-h4', 'text-h5', 'text-h6',
        'text-subtitle-1', 'text-subtitle-2', 'text-body-1', 'text-body-2',
        'text-button', 'text-caption', 'text-overline'
    ], description="Text type for text-related components.")
    color: str = Field(None, description="Color of the text.")
    triggerEvent: str = Field(None, description="Trigger event to send code to the backend. None for static text.")
