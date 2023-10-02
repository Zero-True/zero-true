Layout 
======

This document aims to explain how the layout behavior works for components in our application.

Default Behavior for Components
-------------------------------

By default, each component is rendered in its own column, taking up the full width available. This is simply the current behavior, 
although this will likely change in the near future. 

Specifying Rows, Cols and Nested Layouts
-----------------------------------------


Zero-True allows you to create complicated nested layouts. These are the docs for columns, rows and layout:

.. autopydantic_model:: zero_true.ZTLayout 
.. autopydantic_model:: zero_true.ZTRow 
.. autopydantic_model:: zero_true.ZTColumn


Note that Row and Column components can only be used insed of a layout or they will not be rendered. 

Mixed Layouts
-------------

If some components are placed in a layout and others are not, the layout will accommodate both:

1. Components with specified `row` and `column` values will be laid out first, following the order defined by these values.
2. Components without `row` and `column` specified will be added to the layout at the bottom, each taking up its own row.

This approach ensures that you have the flexibility to create complex layouts while keeping the default behavior simple and intuitive.

Example
-------

Here is an example with actual code that shows how the layout works.

.. code-block:: python 

    import zero_true as zt



    slider = zt.Slider(id='slider',label='First Slider')

    if slider.value < 50:
        color = 'primary'
    else:
        color = 'accent'
    slider2 = zt.Slider(id='slider3',color=color,label='Third Slider')

    slider1 = zt.RangeSlider(id='slider1',color=color, label= 'Second Slider')


    slider4 = zt.Slider(id='slider4',label = 'Fourth Slider')

    button = zt.Button(id='btn',text ='Only Button')

    # Create nested rows
    nested_row1 = zt.ZTRow(id='nested_row1', columns=[
        zt.ZTColumn(id='nested_col1_1', components=['slider4']),
        zt.ZTColumn(id='nested_col1_2', components=['btn'])
    ])

    nested_row2 = zt.ZTRow(id='nested_row2', columns=[
        zt.ZTColumn(id='nested_col2_1', components=['slider1']),
    ])

    # Main layout
    layout_example = zt.ZTLayout(rows=[
        zt.ZTRow(id='row1', columns=[
            zt.ZTColumn(id='col1', components=['slider', 'slider3',nested_row2]),
            zt.ZTColumn(id='col2', components=[nested_row1]),
        ]),
    ])

And this is the resulting layout:

.. image:: assets/example_layout.png 
    