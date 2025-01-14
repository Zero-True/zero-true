from pydantic import Field, BaseModel
from typing import List, Dict, Any
from zt_backend.models.components.zt_component import ZTComponent


class Header(BaseModel):
    """Header class for the columns of a DataFrame component"""

    title: str = Field("", description="Title of the column")
    align: str = Field("start", description="Alignment of values in the column")
    key: str = Field(
        "name", description="Key of the column, must match the key in the items list"
    )


class DataFrame(ZTComponent):
    """DataFrame component for displaying tabular data"""

    component: str = Field("v-data-table", description="Vue component name.")
    headers: List[Header] = Field(
        [], description="List of column headers for the DataFrame"
    )
    items: List[Dict[str, Any]] = Field(
        [], description="List of items to be displayed in the DataFrame"
    )
    multi_sort: bool = Field(
        True, description="Enable or disable multi-sort on the DataFrame"
    )
    style: str = Field("", description="CSS style to apply to the component")
    search: str = Field(
        "",
        description="Create a text_input component search = zt.text_input(id='search') before to filter the DataFrame items",
    )

    @classmethod
    def from_dataframe(cls, df, id: str, multi_sort: bool = True, search: str = ""):
        """Create a DataFrame component from a pandas DataFrame."""
        # Check if pandas / numpy are installed
        try:
            import pandas as pd
            import numpy as np
        except ImportError as e:
            raise ImportError(
                "pandas or numpy is not installed. Please install with 'pip install pandas numpy'."
            ) from e

        if not isinstance(df, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame")

        # Replace NaN/inf values
        df = df.replace({np.nan: None, np.inf: None, -np.inf: None})

        # Filter rows if a search string is provided
        if search:
            search = search.lower()
            df = df[
                df.astype(str)
                .apply(lambda x: x.str.lower().str.contains(search))
                .any(axis=1)
            ]

        # Create headers/items from the DataFrame
        headers = [{"title": col, "key": col} for col in df.columns]
        items = df.to_dict(orient="records")

        return cls(
            id=id, headers=headers, items=items, multi_sort=multi_sort, search=search
        )


def dataframe(df, id: str, multi_sort: bool = True, search: str = ""):
    """Create a ZT DataFrame component from a pandas DataFrame."""
    # Check if pandas / numpy are installed
    try:
        import pandas as pd
        import numpy as np
    except ImportError as e:
        raise ImportError(
            "pandas or numpy is not installed. Please install with 'pip install pandas numpy'."
        ) from e

    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")

    # Replace NaN/inf values
    df = df.replace({np.nan: None, np.inf: None, -np.inf: None})

    # Filter rows if a search string is provided
    if search:
        search = search.lower()
        df = df[
            df.astype(str)
            .apply(lambda x: x.str.lower().str.contains(search))
            .any(axis=1)
        ]

    # Create headers/items from the DataFrame
    headers = [{"title": col, "key": col} for col in df.columns]
    items = df.to_dict(orient="records")

    return DataFrame(
        id=id, headers=headers, items=items, multi_sort=multi_sort, search=search
    )
