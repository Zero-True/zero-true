from pydantic import Field
from zt_backend.models.components.zt_component import ZTComponent

class HTML(ZTComponent):
    """This is a component is used to render arbitrary HTML"""
    component: str = Field("zt-html", description="Vue component name")
    v_html: str = Field('', description="HTML content of the div")