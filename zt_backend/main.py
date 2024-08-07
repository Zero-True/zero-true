from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from zt_backend.config import settings
from zt_backend.utils.notebook import get_notebook, write_notebook
from zt_backend.utils.dependencies import parse_dependencies, write_dependencies
from copilot.copilot import copilot_app
import zt_backend.router as router
import os
import webbrowser
import logging
import traceback
import pkg_resources
import matplotlib

app = FastAPI()
logger = logging.getLogger("__name__")

current_path = os.path.dirname(os.path.abspath(__file__))

run_mode = settings.run_mode
project_name = settings.project_name
user_name = settings.user_name
local_url = settings.local_url

app.include_router(router.router)
app.mount("/copilot", copilot_app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.on_event("startup")
def open_project():
    try:
        matplotlib.use("Agg")
        if not os.path.exists("notebook.ztnb"):
            logger.info("No notebook file found, creating with empty notebook")
            write_notebook()
        if not os.path.exists("requirements.txt"):
            logger.info("No requirements file found, creating with base dependency")
            with open("requirements.txt", "w") as file:
                file.write(
                    f"zero-true=={pkg_resources.get_distribution('zero-true').version}"
                )
        else:
            write_dependencies(parse_dependencies())
        get_notebook()
        if local_url:
            webbrowser.open(local_url)
    except Exception as e:
        logger.error("Error creating new files on startup: %s", traceback.format_exc())


if run_mode == "app":
    app.mount(
        "",
        StaticFiles(directory=os.path.join(current_path, "dist_app"), html=True),
        name="assets",
    )
else:
    app.mount(
        "",
        StaticFiles(directory=os.path.join(current_path, "dist_dev"), html=True),
        name="assets",
    )
