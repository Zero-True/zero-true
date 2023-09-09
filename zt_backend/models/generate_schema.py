from zt_backend.models import *

def generate_json(model, name):
    with open('zt_schema/'+name+'.json', 'w+') as file:
        file.write(model.schema_json(indent=2))

def generate_schema():
    generate_json(Request, 'request')
    generate_json(Response, 'response')
    generate_json(Slider, 'slider')
