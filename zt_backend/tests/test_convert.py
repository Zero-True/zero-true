import convert_ztnb_cell

def test_ipynb_to_ztnb():

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

    with open('notebook.ztnb', "r") as project_file:
        toml_data = rtoml.loads(project_file.read().replace('\\','\\\\'))

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

    
