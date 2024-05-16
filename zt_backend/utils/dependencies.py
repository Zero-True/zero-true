from ast import parse
from fastapi import WebSocket
from zt_backend.models.api import request
from zt_backend.models import notebook
import subprocess
import logging
import traceback
import pkg_resources

logger = logging.getLogger("__name__")


def parse_dependencies():
    dependencies = []
    with open("requirements.txt", "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                try:
                    package, version = line.strip().split("==")
                    if package != "zero-true":
                        dependencies.append(
                            notebook.Dependency(package=package, version=version)
                        )
                except:
                    package = line.strip()
                    if package != "zero-true":
                        dependencies.append(
                            notebook.Dependency(package=package, version="")
                        )
    return notebook.Dependencies(dependencies=dependencies)


def check_env(dependencies: notebook.Dependencies):
    for dependency in dependencies.dependencies:
        if not check_installed(dependency.package, dependency.version):
            return False
    return True


def write_dependencies(dependencies: notebook.Dependencies):
    with open("requirements.txt", "w", encoding="utf-8") as file:
        file.seek(0)
        file.write(f"zero-true=={pkg_resources.get_distribution('zero-true').version}\n")
        for dependency in dependencies.dependencies:
            if dependency.package:
                if dependency.version:
                    file.write(f"{dependency.package}=={dependency.version}\n")
                else:
                    file.write(f"{dependency.package}\n")
        file.truncate()


def check_installed(package, version):
    try:
        dist = pkg_resources.get_distribution(package)
        if version:
            return dist.version == version
        return True
    except:
        return False


async def dependency_update(
    dependency_request: request.DependencyRequest, websocket: WebSocket
):
    try:
        for dependency in dependency_request.dependencies.dependencies:
            if not check_installed(dependency.package, dependency.version):
                command = ["pip", "install"]
                if dependency.version:
                    command.append(f"{dependency.package}=={dependency.version}")
                else:
                    command.append(dependency.package)
                with subprocess.Popen(
                    command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
                ) as process:
                    for line in process.stdout:
                        await websocket.send_json({"output": line})
                    process.stdout.close()
                    return_code = process.wait()
                    if return_code != 0:
                        return parse_dependencies()
        write_dependencies(dependency_request.dependencies)
        subprocess.run(["lock", "requirements.txt"])
        return parse_dependencies()
    except Exception as e:
        logger.error("Error updating dependencies: %s", traceback.format_exc())
