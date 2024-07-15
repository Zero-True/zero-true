from zt_backend.models.api import request
import subprocess

def dependency_update(dependencyRequest: request.DependencyRequest):
    with open('requirements.txt', 'r+', encoding='utf-8') as file:
        contents = file.read()
        if contents == dependencyRequest.dependencies:
            return "No change to dependencies"
        file.seek(0)
        file.write(dependencyRequest.dependencies)
        file.truncate()
    subprocess.run(['pip', 'install', '-r', 'requirements.txt'])
    subprocess.run(['lock', 'requirements.txt'])