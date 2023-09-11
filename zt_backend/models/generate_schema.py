from zt_backend.models import *
from fastapi.encoders import jsonable_encoder
import json

def generate_json(model, name):
    with open('zt_schema/'+name+'.json', 'w+') as file:
        file.write(json.dumps(model.model_json_schema(),indent=2))

def generate_schema():
    generate_json(Request, 'request')
    generate_json(Response, 'response')
    generate_json(Slider, 'slider')
    generate_json(Notebook, 'notebook')
