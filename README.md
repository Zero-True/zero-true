![Zero True Logo](zt_frontend/src/assets/logo.png)

# Zero True: A New Kind of Code Notebook



## 🌐 Overview

Welcome to **Zero True**, your go-to platform for creating beautiful and professional data-driven notebooks and applications in pure Python. Designed to foster collaboration and improve data accessibility, Zero True offers a rich UI library along with an intelligent code parser. Your notebook will always stay in sync.

## 📚 Table of Contents

- [Features](#-features)
- [Requirements](#-requirements)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
- [Community](#-community)

## Features

- 📝 Multi-language code editor with real-time execution.
- 🌌 Hierarchical organization for code cells.
- 📊 Dynamic UI rendering with beautiful [Vuetify](https://vuetifyjs.com/en/) components.
- 🔄 Automatic dependency tracking between cells.
- 🚀 Integrated app publishing with a simple command or click.


## ⚙ Requirements

- Python 3.9 (Anaconda or virtual environment recommended)

## 🚀 Quick Start

```bash
pip install zero-true
zero-true notebook
```

### Usage 

Once the application is running, navigate to http://localhost:2613 and start creating and executing code cells. Click the "Run" button to execute code and visualize the output below the editor. 

#### Basic Example

```python
import zero_true as zt
my_slider = zt.Slider(id="my_slider")
```


#### More Complicated Example

```python

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


```

And the resulting layout:

![More Complicated Example](/docs/assets/example_layout.png)


For more information checkout our [docs](https://docs.zero-true.com/)!


### Community

Reach out on GitHub with any feature requests or bugs that you encounter and share your work with us on Twitter/X! We would love to see what you're able to build using Zero-True. 