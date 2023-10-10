from pydantic import Field
from zt_backend.models.components.zt_component import ZTComponent
from typing import Dict
from plotly.graph_objs import Figure
import pandas as pd
import numpy as np

def convert_special_types(obj):
    """Recursively convert special types like DataFrame and NumPy array to list."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, (pd.DataFrame, np.ndarray)):
                obj[key] = value.tolist()
            else:
                convert_special_types(value)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            if isinstance(item, (pd.DataFrame, np.ndarray)):
                obj[i] = item.tolist()
            else:
                convert_special_types(item)

class PlotlyComponent(ZTComponent):
    component: str = Field("plotly-plot", description="Vue component name for Plotly.")
    figure: Dict = Field(..., description="Plotly figure object.")
    layout: dict = Field(..., description="Layout for Plotly plot.")
    id: str = Field(..., description="ID for the component")
    
    @classmethod
    def from_figure(cls, figure: Figure, id: str):
        """Creates a PlotlyComponent instance from a Plotly figure object."""
        figure.update_layout(template = 'plotly_dark')
        # Ensure the input is a Plotly figure
        if not isinstance(figure, Figure):
            raise ValueError("Input must be a Plotly Figure")
        # Convert the figure to JSON-serializable dictionary
        figure_json = figure.to_plotly_json()
        figure_data = figure_json.get('data', [])
        layout_data = figure_json['layout']
        #print(layout_data)
        # Convert any special types like DataFrame or NumPy array to list
        for trace in figure_data:
            convert_special_types(trace)
        return cls(figure=figure_json, layout=layout_data, id=id)
    
    def to_json(self):
        """Converts the Plotly figure to a JSON-serializable dictionary."""
        return {
            "component": self.component,
            "figure": self.figure,
            "layout": self.layout,
            "id": self.id
        }