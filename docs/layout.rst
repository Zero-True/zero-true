Layout 
======

This document aims to explain how the layout behavior works for components in our application.

Default Behavior for Components
-------------------------------

By default, each component is rendered in its own column, taking up the full width available. This is simply the current behavior, 
although this will likely change in the near future. 

Specifying Rows and Columns
---------------------------

If you specify both a `row` and `column` for a component, the component will be positioned accordingly within the layout grid. Components will appear in the order defined by the `row` and `column` values.

For example:

- A component with `row=1` and `column=1` will appear in the first row and first column.
- A component with `row=1` and `column=2` will appear in the first row and second column, right next to the first component.


Mixed Layouts
-------------

If some components have `row` and `column` specified while others do not, the layout will accommodate both:

1. Components with specified `row` and `column` values will be laid out first, following the order defined by these values.
2. Components without `row` and `column` specified will be added to the layout at the bottom, each taking up its own row.

This approach ensures that you have the flexibility to create complex layouts while keeping the default behavior simple and intuitive.

Example
-------

Here is an example with actual code that shows how the layout works.

.. code-block:: python 

    from zt_backend.models.components.slider import Slider 
    from zt_backend.models.components.range_slider import RangeSlider
    from zt_backend.models.components.button import Button 

    slider = Slider(id='slider',row=0,column=0,label='First Slider')

    if slider.value < 50:
        color = 'primary'
    else:
        color = 'accent'
        
    slider1 = RangeSlider(id='slider1',color=color,row=0,column=0, label= 'Second Slider')
    slider2 = Slider(id='slider3',color=color,row=2,column=0,label='Third Slider')
    slider4 = Slider(id='slider4',label = 'Fourth Slider')

    button = Button(id='btn',text = 'Only Button')

And this is the resulting layout:

.. image:: assets/example_layout.png 
    