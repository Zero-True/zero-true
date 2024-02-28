import pandas as pd
from pydantic import Field, BaseModel
import numpy as np
from zt_backend.models.components.zt_component import ZTComponent
from typing import List, Dict,Any


class Header(BaseModel):
    """Header class for the columns of a DataFrame component"""
    title: str = Field("", description="Title of the column")
    align: str = Field("start", description="Alignment of values in the column")
    key: str = Field("name", description="Key of the column, must match the key in the items list")

class DataFrame(ZTComponent):
    """DataFrame component for displaying tabluar data"""
    component: str = Field("v-data-table", description="Vue component name.")
    headers: List[Header] = Field([], description="List of column headers for the DataFrame")
    items: List[Dict[str, Any]] = Field([], description="List of items to be displayed in the DataFrame")

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame, id: str):
        """Create a DataFrame component from a pandas DataFrame"""
        df = df.replace({np.nan:None}).replace({np.inf:None}).replace({-np.inf:None})
        headers = [{"title": col, "key": col} for col in df.columns]
        items = df.to_dict(orient='records')
        return cls(id=id, headers=headers, items=items)