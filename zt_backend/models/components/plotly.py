from pydantic import Field
from zt_backend.models.components.zt_component import ZTComponent
from plotly.graph_objs import Figure
from plotly.io import to_json

def figure_to_json(figure: Figure) -> str:
    """Serializes a Plotly figure to a JSON string."""
    return to_json(figure, validate=False)

class PlotlyComponent(ZTComponent):
    """Component to display a Plotly figure"""
    component: str = Field("plotly-plot", description="Vue component name for Plotly")
    figure_json: str = Field(..., description="Serialized Plotly figure as JSON string")
    id: str = Field(..., description="ID for the component")

    @classmethod
    def from_figure(cls, figure: Figure, id: str):
        """Creates a PlotlyComponent instance from a Plotly figure."""
        figure.update_layout(template='plotly_dark')
        if not isinstance(figure, Figure):
            raise ValueError("Input must be a Plotly Figure")
        figure_json = figure_to_json(figure)  # Serialize figure to JSON
        return cls(figure_json=figure_json, id=id)

    def to_json(self):
        """Converts the component to a JSON-serializable dictionary."""
        return {
            "component": self.component,
            "figureJson": self.figure_json,
            "id": self.id
        }