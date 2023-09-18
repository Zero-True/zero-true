from pydantic import BaseModel
from typing import List, Dict, Union
from zt_backend.models.components.slider import Slider
from zt_backend.models.components.zt_component import ZTComponent

# def deserialize_component(data: Dict[str, Any]) -> ZTComponent:
#     component_map = {
#         "v-slider": Slider,
#         # add other component types here
#     }
#     component_class = data.get("component")
#     if component_class not in component_map:
#         raise ValueError(f"Invalid component class: {component_class}")
#     return component_map[component_class].model_validate(data)

class CodeRequest(BaseModel):
    id: str
    code: str


class Request(BaseModel):
    cells: List[CodeRequest]
    components: Dict[str, Union[str, bool, int]]


class Cell(BaseModel):
    code: str
    defined_names: List[str]
    loaded_names: List[str]
    child_cells: List[int] = []
    parent_cells: List[int] = []
    previous_child_cells: List[int] = []

class CodeDict(BaseModel):
    cells: Dict[str, Cell]


    # @root_validator(pre=True)
    # def deserialize_components(cls, values):
    #     components = values.get('components', [])
    #     values['components'] = [deserialize_component(comp) for comp in components]
    #     return values