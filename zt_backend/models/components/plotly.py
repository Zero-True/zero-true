from pydantic import Field
from zt_backend.models.components.zt_component import ZTComponent
import json

def json_encoder(value):
    return json.dumps(value)



class PlotlyComponent(ZTComponent):
    component: str = Field("plotly-plot", description="Vue component name for Plotly.")
    figure: dict = Field(..., description="Plotly figure object.",json_encoders={dict: json_encoder})
    layout: dict = Field(..., description="Layout for Plotly plot.",json_encoders={dict: json_encoder})

    def to_json(self):
        """Converts the Plotly figure to a JSON-serializable dictionary."""
        return {
            "component": self.component,
            "figure": self.figure,
            "layout": self.layout
        }
