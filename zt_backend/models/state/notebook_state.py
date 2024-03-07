from zt_backend.models.api import request
from zt_backend.models import notebook
from typing import OrderedDict
import site
import uuid
import os

class NotebookState:
    def __init__(self):
        notebook_db_dir =  site.USER_SITE+'/.zero_true/'
        notebook_db_path = notebook_db_dir+'notebook.db'
        os.makedirs(notebook_db_dir, exist_ok=True)

        self.notebook_db_path = notebook_db_path
        codeCell = notebook.CodeCell(
                        id=str(uuid.uuid4()),
                        code='',
                        components=[],
                        variable_name='',
                        output='',
                        cellType='code'
                    )
        self.zt_notebook = notebook.Notebook(userId='', cells=OrderedDict([(codeCell.id, codeCell)]))
        self.base_cells = []
        self.base_components = {}