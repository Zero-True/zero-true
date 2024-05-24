from zt.backend.zt_cli import convert, create_ztnb_cell
from zt_backend.models import notebook
import rtoml

def test_ipynb_to_ztnb():

    with open("./test_file.ipynb.txt", "r", encoding="utf-8") as f: 
        notebook = json.loads(f.read()) 

    output = [] 

    output.append(f'notebookId = "{uuid.uuid4()}"')
    output.append('notebookName = "Zero True"')
    output.append('')
    create_ztnb_cell('"code"', ['import zero-true as zt'], output)

    for cell in notebook['cells']:
        if (cell['cell_type'] == 'code'):
            create_ztnb_cell('"code"', cell['source'], output)
        if (cell['cell_type'] == 'markdown'):
            create_ztnb_cell('"markdown"', cell['source'], output)

    with open("notebook.ztnb", 'w') as f:
        for item in output:
            f.write(item + '\n') 
        toml_data = rtoml.loads(f.read().replace('\\','\\\\'))

    notebook_data = {
        'notebookId' : toml_data['notebookId'],
        'notebookName' : toml_data.get('notebookName', 'Zero True'),
        'userId' : '',
        'cells': {
            cell_id: notebook.CodeCell(id=cell_id, **cell_data, output="")
            for cell_id, cell_data in toml_data['cells'].items()
        }
    }

    notebook_state.zt_notebook = notebook.Notebook(**notebook_data)

    assert notebook_state.zt_notebook.notebookId == toml_data['notebookId']
