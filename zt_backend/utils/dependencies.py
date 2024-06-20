from fastapi import WebSocket
from zt_backend.models.api import request
from zt_backend.models import notebook
import subprocess
import logging
import traceback
import pkg_resources
import re

logger = logging.getLogger("__name__")


def parse_dependencies():
    dependencies = []
    with open("requirements.txt", "r", encoding="utf-8") as file:
        for line in file:
            line = re.sub(r"#.*", "", line).strip()
            if not line:
                continue
            match = re.split(r"([<>=!~]+)", line, 1)
            if match:
                package = match[0].strip()
                if package != "zero-true":
                    version = ""
                    if len(match) > 1:
                        version = version.join(match[1:]).strip()
                    dependencies.append(
                        notebook.Dependency(package=package, version=version)
                    )
    return notebook.Dependencies(dependencies=dependencies)


def check_env(dependencies: notebook.Dependencies):
    for dependency in dependencies.dependencies:
        try:
            pkg_resources.require(f"{dependency.package}{dependency.version}")
        except pkg_resources.DistributionNotFound:
            return False
        except pkg_resources.VersionConflict:
            return False
    return True


def write_dependencies(dependencies: notebook.Dependencies):
    with open("requirements.txt", "w", encoding="utf-8") as file:
        file.seek(0)
        file.write(
            f"zero-true=={pkg_resources.get_distribution('zero-true').version}\n"
        )
        for dependency in dependencies.dependencies:
            if dependency.package:
                file.write(f"{dependency.package}{dependency.version}\n")
        file.truncate()


async def dependency_update(
    dependency_request: request.DependencyRequest, websocket: WebSocket
):
    try:
        write_dependencies(dependency_request.dependencies)
        command = ["pip", "install", "-r", "requirements.txt"]
        with subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        ) as process:
            for line in process.stdout:
                await websocket.send_json({"output": line})
            process.stdout.close()
        return parse_dependencies()
    except Exception as e:
        logger.error("Error updating dependencies: %s", traceback.format_exc())
