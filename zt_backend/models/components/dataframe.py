import pandas as pd
from pydantic import Field
from zt_backend.models.components.zt_component import ZTComponent
from typing import List, Dict

class DataFrame(ZTComponent):
    component: str = Field("v-data-table", description="Vue component name.")
    headers: List[Dict] = Field([], description="Headers for the table.")
    items: List[Dict] = Field([], description="Data for the DataFrame.")

    def __init__(self, df: pd.DataFrame, **data):
        super().__init__(**data)
        self.load_dataframe(df)
        
    def load_dataframe(self, df: pd.DataFrame):
        columns = []
        for i, colname in enumerate(df.columns):
            list_item = {'text': colname, 'value': colname}
            if i != 0:
                list_item['align'] = 'right'
            columns.append(list_item)
        
        self.headers = columns
        self.items = df.to_dict(orient='records')
