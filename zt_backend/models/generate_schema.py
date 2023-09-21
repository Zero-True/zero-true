from .request import Request, ComponentRequest, DeleteRequest, CreateRequest
from .response import Response
from .notebook import Notebook
from .components.slider import Slider
from .components.text_input import TextInput
import json

def generate_json(model, name):
    with open('zt_schema/'+name+'.json', 'w+') as file:
        file.write(json.dumps(model.model_json_schema(),indent=2))

def generate_schema():
    generate_json(Request, 'request')
    generate_json(ComponentRequest, 'component_request')
    generate_json(DeleteRequest, 'delete_request')
    generate_json(CreateRequest, 'create_request')
    generate_json(Response, 'response')
    generate_json(Slider, 'slider')
    generate_json(Notebook, 'notebook')
    generate_json(TextInput, 'text_input')
