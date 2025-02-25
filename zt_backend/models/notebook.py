from fastapi import dependencies
from pydantic import BaseModel, Field, SerializeAsAny, model_validator
from typing import OrderedDict, List, Dict, Any, ForwardRef
from uuid import uuid4
from zt_backend.models.components.zt_component import ZTComponent
from zt_backend.models.components.slider import Slider
from zt_backend.models.components.rating import Rating
from zt_backend.models.components.text_input import TextInput
from zt_backend.models.components.file_input import FileInput
from zt_backend.models.components.text_area_input import TextArea
from zt_backend.models.components.range_slider import RangeSlider
from zt_backend.models.components.selectbox import SelectBox
from zt_backend.models.components.button import Button
from zt_backend.models.components.number_input import NumberInput
from zt_backend.models.components.image import Image
from zt_backend.models.components.text import Text
from zt_backend.models.components.dataframe import DataFrame
from zt_backend.models.components.layout import Layout
from zt_backend.models.components.plotly import PlotlyComponent
from zt_backend.models.components.autocomplete import Autocomplete
from zt_backend.models.components.card import Card
from zt_backend.models.components.timer import Timer

Comment = ForwardRef("Comment")


def deserialize_component(data: Dict[str, Any]) -> ZTComponent:
    component_map = {
        "v-slider": Slider,
        "v-rating": Rating,
        "v-text-field": TextInput,
        "v-file-input": FileInput,
        "v-textarea": TextArea,
        "v-number-input": NumberInput,
        "v-range-slider": RangeSlider,
        "v-select": SelectBox,
        "v-btn": Button,
        "v-img": Image,
        "v-text": Text,
        "v-data-table": DataFrame,
        "v-autocomplete": Autocomplete,
        "v-card": Card,
        "v-timer": Timer,
        "plotly-plot": PlotlyComponent,
        # add other component types here
    }
    component_class = data.get("component")
    if component_class not in component_map:
        raise ValueError(f"Invalid component class: {component_class}")
    return component_map[component_class].model_validate(data)


class CodeCell(BaseModel):
    id: str
    code: str
    output: str
    cellName: str = Field("")
    hideCell: bool = Field(False)
    hideCode: bool = Field(False)
    expandCode: bool = Field(False)
    showTable: bool = Field(False)
    nonReactive: bool = Field(False)
    variable_name: str = Field("")
    layout: Layout = Field(Layout())
    components: List[SerializeAsAny[ZTComponent]]
    cellType: str = Field(enum=["code", "markdown", "text", "sql"])
    comments: OrderedDict[str, Comment] = Field({})

    @model_validator(mode="before")
    def deserialize_components(cls, values):
        components = values.get("components", [])
        values["components"] = [deserialize_component(comp) for comp in components]
        return values


class Notebook(BaseModel):
    notebookName: str = Field("Zero True")
    notebookId: str = Field(default=str(uuid4()))  # Added notebook UUID
    cells: OrderedDict[str, CodeCell]
    userId: str
    wideMode: bool = Field(False)


class Dependency(BaseModel):
    package: str
    version: str = Field("")


class Dependencies(BaseModel):
    dependencies: List[Dependency] = Field([])


class Comment(BaseModel):
    id: str
    comment: str
    date: str
    replies: OrderedDict[str, Comment] = Field({})
    resolved: bool = Field(False)


class NotebookResponse(BaseModel):
    notebook: Notebook
    dependencies: Dependencies
