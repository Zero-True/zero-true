import os
import sys
sys.path.insert(0, os.path.abspath('../'))


extensions = [
    'sphinxcontrib.autodoc_pydantic',
]
html_theme = 'furo'
html_favicon = '../zt_frontend/src/assets/favicon.ico'
