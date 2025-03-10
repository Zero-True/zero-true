import zero_true as zt

def cell_0():
    print('Hello, world!')

def cell_1():
    zt.markdown("""# This is a markdown cell""")

notebook = zt.notebook(
    id='ca156d73-1c20-48c6-afbb-ae177c6bafa5',
    name='Zero True',
    cells=[
        zt.cell(cell_0, type='code'),
        zt.cell(cell_1, type='markdown'),
    ]
)
