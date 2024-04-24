import os
import sys

sys.path.insert(0, os.path.abspath('../'))

# Create the _static directory if it doesn't exist

project = 'Zero-True'

extensions = [
    'sphinxcontrib.autodoc_pydantic',
]

html_theme = 'furo'

html_title = 'Zero-True documentation'  # Change this line to set your title

html_favicon = '../zt_frontend/public/favicon.ico'

html_css_files = ['custom_theme.css']
