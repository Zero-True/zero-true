from pydantic import BaseModel, root_validator
from typing import List, Dict, Any
from zt_backend.models.components.slider import Slider
from zt_backend.models.components.zt_component import ZTComponent

def deserialize_component(data: Dict[str, Any]) -> ZTComponent:
    component_map = {
        "v-slider": Slider,
        # add other component types here
    }
    component_class = data.get("component")
    if component_class not in component_map:
        raise ValueError(f"Invalid component class: {component_class}")
    return component_map[component_class].model_validate(data)

class CodeRequest(BaseModel):
    id: str
    code: str

class Request(BaseModel):
    cells: List[CodeRequest]
    components: List[ZTComponent]

    @root_validator(pre=True)
    def deserialize_components(cls, values):
        components = values.get('components', [])
        values['components'] = [deserialize_component(comp) for comp in components]
        return values