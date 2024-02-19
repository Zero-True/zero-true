from pydantic import Field, field_validator, validator
from zt_backend.models.components.zt_component import ZTComponent
from zt_backend.models.validations import validate_color
from typing import Optional, Union
from zt_backend.runner.user_state import UserContext

class ipywidgets(ZTComponent):
    """A slider component that allows you to capture numeric input from a user. 
    
    To use the slider simply import the package and then declare the slider. The only required 
    field is an id. Your slider will render with default max and min values and a number 
    of other defaults.
    
    """
    component: str = Field("v-ipywidgets", description="Vue component name.")
    widget:  dict = Field({}, description="ipywidget object")
    
    