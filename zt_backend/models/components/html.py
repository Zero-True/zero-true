from pydantic import Field
from typing import Union
from zt_backend.models.components.zt_component import ZTComponent
import pandas as pd

class HTML(ZTComponent):
    """This is a component is used to render arbitrary HTML"""
    component: str = Field("zt-html", description="Vue component name")
    v_html: str = Field("", description="HTML content of the component")

def pygwalker(id: str, df: pd.DataFrame, width: Union[int, str] = '100%', height: Union[int, str] = 920):
    """Create a PyGWalker component from a pandas DataFrame"""
    try:
        import pandas as pd
        import pygwalker as pyg
    except ImportError as e:
        raise ImportError(
            "pygwalker or pandas is not installed. Please install with 'pip install pygwalkwer'."
        ) from e
        
    return HTML(id=id, v_html=pyg.to_html(df, width=width, height=height))