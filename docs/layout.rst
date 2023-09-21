Layout 
======

This document aims to explain how the layout behavior works for components in our application.

Default Behavior for Components
-------------------------------

By default, each component is rendered in its own row, taking up the full width available.

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
