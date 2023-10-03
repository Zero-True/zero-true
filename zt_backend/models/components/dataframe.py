import pandas as pd
from pydantic import Field, validator, BaseModel

from zt_backend.models.components.zt_component import ZTComponent
from typing import List, Dict,Any


class Header(BaseModel):
    title: str
    align: str = Field("start", description="Column alignment.")
    key: str = 'name'

class DataFrame(ZTComponent):
    component: str = "v-data-table"
    headers: List[Header] 
    items: List[Dict[str, Any]]

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame, id: str):
        headers = [{"title": col, "key": col} for col in df.columns]
        items = df.to_dict(orient='records')
        return cls(id=id, headers=headers, items=items)