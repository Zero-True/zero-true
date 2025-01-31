from fastapi import WebSocket
from zt_backend.models.api import request
from zt_backend.models import notebook
import subprocess
import logging
import traceback
from importlib.metadata import version, PackageNotFoundError
import re
from pathlib import Path
from zt_backend.config import settings
import sys
from packaging.version import Version
from packaging.specifiers import SpecifierSet

logger = logging.getLogger("__name__")


def parse_dependencies():
    dependencies = []
    requirements_path = Path(settings.zt_path) / "requirements.txt"
    with requirements_path.open("r", encoding="utf-8") as file:
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
        package_name = dependency.package
        required_version = dependency.version
        try:
            installed_version = Version(version(package_name))
            if required_version and not installed_version in SpecifierSet(
                required_version
            ):
                return f"Requirement {package_name}{required_version} not met. Installed version of {package_name} is {installed_version}."
        except PackageNotFoundError:
            return f"Dependency {package_name} is not installed."
    return None


def write_dependencies(dependencies: notebook.Dependencies):
    requirements_path = Path(settings.zt_path) / "requirements.txt"
    with requirements_path.open("w", encoding="utf-8") as file:
        for dependency in dependencies.dependencies:
            if dependency.package and dependency.version:
                # Write package with specified version
                file.write(f"{dependency.package}{dependency.version}\n")
            elif dependency.package:
                try:
                    # Get installed version of the package
                    installed_version = version(dependency.package)
                    file.write(f"{dependency.package}=={installed_version}\n")
                except PackageNotFoundError:
                    # Package not found, write only the package name
                    file.write(f"{dependency.package}\n")


async def dependency_update(
    dependency_request: request.DependencyRequest, websocket: WebSocket
):
    try:
        write_dependencies(dependency_request.dependencies)
        requirements_path = Path(settings.zt_path) / "requirements.txt"
        command = [sys.executable, "-m", "pip", "install", "-r", str(requirements_path)]
        with subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        ) as process:
            for line in process.stdout:
                await websocket.send_json({"output": line})
            process.stdout.close()
        write_dependencies(dependency_request.dependencies)
        if any(
            dep[0].startswith("matplotlib") for dep in dependency_request.dependencies
        ):
            try:
                import matplotlib

                matplotlib.use("Agg")
            except Exception as e:
                logger.info("matplotlib not found")
        return parse_dependencies()
    except Exception as e:
        logger.error("Error updating dependencies: %s", traceback.format_exc())
