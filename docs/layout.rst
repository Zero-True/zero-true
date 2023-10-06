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

.. autopydantic_model:: zero_true.Layout 
.. autopydantic_model:: zero_true.Row 
.. autopydantic_model:: zero_true.Column


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

    import plotly.graph_objects as go
    from plotly.graph_objects import Figure
    import zero_true as zt


    # Generate a layout
    layout = {
        "title": "My Plot",
        "xaxis": {"title": "x-axis"},
        "yaxis": {"title": "y-axis"}
    }

    slider=zt.Slider(id='slider1')
    zt.Slider(id='slider2')
    zt.Slider(id='slider3')
    zt.Slider(id='slider4')
    zt.Slider(id='slider5')

    fig = go.Figure(data=[go.Scatter(x=[slider.value, slider.value+2, slider.value+3], y=[1, 4, 9])])

    zt.PlotlyComponent(id = 'acds',figure=fig.to_dict(), layout=layout)

    zt.Layout(rows=[zt.Row(components=['slider3',zt.Column(components=['slider4','slider5'])])],columns=[zt.Column(components=['acds','slider1']),
                        zt.Column(components=['slider2'])])

And this is the resulting layout:

.. image:: assets/example_layout.png 
    