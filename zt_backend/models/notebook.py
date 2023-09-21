from pydantic import BaseModel, Field, SerializeAsAny, model_validator
from typing import OrderedDict, List, Dict, Any
from zt_backend.models.components.zt_component import ZTComponent
from zt_backend.models.components.slider import Slider
from zt_backend.models.components.text_input import TextInput

def deserialize_component(data: Dict[str, Any]) -> ZTComponent:
    component_map = {
        "v-slider": Slider,
        "v-text-field":TextInput
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
    components: List[SerializeAsAny[ZTComponent]]
    cellType: str = Field(enum=['code', 'markdown', 'text'])

    @model_validator(mode='before')
    def deserialize_components(cls, values):
        components = values.get('components', [])
        values['components'] = [deserialize_component(comp) for comp in components]
        return values
    
class Notebook(BaseModel):
    cells: OrderedDict[str, CodeCell]


