Layout 
======

This document aims to explain how the layout behavior works for components in Zero-True. Defining a 
layout is optional but provides a way to explicitly define the position of components defined in a cell.
By default, each component is rendered in its own row, taking up the full width available. 

Specifying Rows, Cols and Nested Layouts
-----------------------------------------


Zero-True allows you to create complicated nested layouts. These are the docs for columns, rows, and the layout:

.. autopydantic_model:: zero_true.Layout 
    :model-show-field-summary: false
    :model-show-validator-summary: false
.. autopydantic_model:: zero_true.Row 
    :model-show-field-summary: false
    :model-show-validator-summary: false
.. autopydantic_model:: zero_true.Column
    :model-show-field-summary: false
    :model-show-validator-summary: false

Note that Row and Column components can only be used as part of a layout or another row/column or they will not be rendered. 

Mixed Layouts
-------------

If some components are placed in a layout and others are not, the layout will accommodate both:

1. Rows will be rendered first in the order they are added to the rows list of the layout.
2. Columns will be rendered next in the order they are added to the columns list of the layout. Each column not placed inside of a row will be placed in its own row and take up the available width.
3. All other components not in a row or column will then be rendered in the order they are defined in code and take up the full width available, each in their own row.

Example
-------

Here is an example with actual code that shows how the layout works:

.. code-block:: python 

    import zero_true as zt

    image = zt.Image(id='image', src='https://www.escapemotions.com/images/mainpage/images/blog_posts_bg/landing-page_blog_93303113643.jpg', width=500, height=300)
    
    slider = zt.Slider(id='slider', label='slider')
    slider2 = zt.Slider(id='slider2', label='slider2')
    slider3 = zt.Slider(id='slider3', label='slider3')
    slider4 = zt.Slider(id='slider4', label='slider4')
    slider5 = zt.Slider(id='slider5', label='slider5')
    
    button = zt.Button(id='button', text='button')
    button2 = zt.Button(id='button2', text='button2')
    button3 = zt.Button(id='button3', text='button3')
    button4 = zt.Button(id='button4', text='button4')
    button5 = zt.Button(id='button5', text='button5')

    col = zt.Column(components=['slider', 'button'])
    row = zt.Row(components=['image', 'slider2', 'button2', col])
    col2 = zt.Column(components=['slider4', 'button4'])
    row2 = zt.Row(components=['slider3', 'button3', col2])
    col3 = zt.Column(components=['slider5', row2])

    zt.Layout(rows=[row], columns=[col3])

And this is the resulting layout:

.. image:: assets/example_layout.png 
    