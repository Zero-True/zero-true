from pydantic import Field
from zt_backend.models.components.zt_component import ZTComponent


def figure_to_json(figure) -> str:
    """
    Serializes a Plotly figure to a JSON string.
    Raises an ImportError if Plotly is not installed.
    """
    try:
        from plotly.io import to_json
        from plotly.graph_objs import Figure
    except ImportError as e:
        raise ImportError("Plotly is not installed. Please install it with 'pip install plotly'") from e
    
    if not isinstance(figure, Figure):
        raise ValueError("Input must be a Plotly Figure")

    return to_json(figure, validate=False)


class PlotlyComponent(ZTComponent):
    """
    Component to display a Plotly figure.
    """
    component: str = Field("plotly-plot", description="Vue component name for Plotly")
    figure_json: str = Field(..., description="Serialized Plotly figure as JSON string")
    id: str = Field(..., description="ID for the component")

    @classmethod
    def from_figure(cls, figure, id: str):
        """
        Creates a PlotlyComponent instance from a Plotly figure.
        Raises an ImportError if Plotly is not installed.
        """
        try:
            from plotly.graph_objs import Figure
        except ImportError as e:
            raise ImportError("Plotly is not installed. Please install it with 'pip install plotly'") from e

        if not isinstance(figure, Figure):
            raise ValueError("Input must be a Plotly Figure")

        # Example of customizing layout
        figure.update_layout(template='plotly_dark')
        
        # Serialize figure to JSON
        figure_json = figure_to_json(figure)
        return cls(figure_json=figure_json, id=id)

    def to_json(self):
        """
        Converts the component to a JSON-serializable dictionary.
        """
        return {
            "component": self.component,
            "figureJson": self.figure_json,
            "id": self.id
        }


def plotlyComponent(id: str, figure):
    """
    Creates a PlotlyComponent instance from a Plotly figure.
    Raises an ImportError if Plotly is not installed.
    """
    try:
        from plotly.graph_objs import Figure
    except ImportError as e:
        raise ImportError("Plotly is not installed. Please install it with 'pip install plotly'") from e

    if not isinstance(figure, Figure):
        raise ValueError("Input must be a Plotly Figure")

    figure.update_layout(template='plotly_dark')
    figure_json = figure_to_json(figure)  # Serialize figure to JSON
    return PlotlyComponent(id=id, figure_json=figure_json)
