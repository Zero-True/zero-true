UI Components
=============

The Zero-True notebook comes with a builtin UI library that aims for the following features:

- **Ease of Use**: Zero True is designed to be straightforward and intuitive, enabling users to build applications without a steep learning curve.
- **Pythonic**: Built for Python developers, Zero True allows you to build web applications using familiar Python syntax.
- **Highly Customizable**: With a range of UI components and layout options, Zero True offers high levels of customization to make your application truly unique.
- **Reactive and Dynamic**: The UI components are built to be reactive, updating in real-time as data changes, providing a dynamic user experience.


Zero-True is still in an alpha development phase and will be adding new components often so please feel free to revisit this page on a periodic basis to make sure
that you are using the latest and greatest UI compoents available.

Explore the detailed API documentation for Zero True, including component properties, utility functions, and more.


Component Reference
-------------------

Zero-True offers an extensive UI componentent library to allow users to build complicated, reactive UIs with only simple python syntax. 
This includes static components to diplay stuff like links and images as well as components that allow users to submit input to the backend.


Static Components
-----------------

.. autopydantic_model:: zero_true.Text 

.. autopydantic_model:: zero_true.Image 

.. autopydantic_model:: zero_true.DataFrame

Input Components
----------------

We have a number of components dedicated to collecting numeric input. 

.. autopydantic_model:: zero_true.Slider

.. autopydantic_model:: zero_true.RangeSlider 

.. autopydantic_model:: zero_true.NumberInput

Users also have the ability to input text through a text input and text area if the required input is more lenghty. 

.. autopydantic_model:: zero_true.TextInput

.. autopydantic_model:: zero_true.TextArea

Users can also input options from preselected lists with the select and multiselect componetents. 

.. autopydantic_model:: zero_true.MultiSelectBox

*There is currently a bug with the MultiSelect component*

.. autopydantic_model:: zero_true.SelectBox

The button can be used to send boolean inputs to the backend. 

.. autopydantic_model:: zero_true.Button 

*There is currentl a bug with the button component.*

