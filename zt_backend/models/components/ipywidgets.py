from pydantic import Field
from zt_backend.models.components.zt_component import ZTComponent

class IPyWidgets(ZTComponent):
    """"""
    component: str = Field("ipywidgets", description="Vue component name.")
    widget:  dict = Field({}, description="ipywidget object")