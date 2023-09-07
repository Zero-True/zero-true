import pydantic
from zt_backend.models.request import Request
import os

def generate_json(model, name):
    print(os.getcwd())
    with open('zt_schema/'+name+'.json', 'w+') as file:
        file.write(model.schema_json(indent=2))

def generate_schema():
    generate_json(Request, 'request')
