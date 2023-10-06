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

    import plotly.graph_objects as go
    from plotly.graph_objects import Figure
    import zero_true as zt


    # Generate a layout
    layout = {
        "title": "My Plot",
        "xaxis": {"title": "x-axis"},
        "yaxis": {"title": "y-axis"}
    }

    heyo=zt.Slider(id='ayo')
    zt.Slider(id='ayo2')
    zt.Slider(id='ayo3')
    zt.Slider(id='ayo4')
    zt.Slider(id='ayo5')

    fig = go.Figure(data=[go.Scatter(x=[heyo.value, heyo.value+2, heyo.value+3], y=[1, 4, 9])])

    zt.PlotlyComponent(id = 'acds',figure=fig.to_dict(), layout=layout)

    zt.Layout(rows=[zt.Row(components=['ayo3',zt.Column(components=['ayo4','ayo5'])])],columns=[zt.Column(components=['acds','ayo']),
                        zt.Column(components=['ayo2'])])


```

And the resulting layout:

![More Complicated Example](/docs/assets/example_layout.png)


For more information checkout our [docs](https://docs.zero-true.com/)!


### Community

Reach out on GitHub with any feature requests or bugs that you encounter and share your work with us on Twitter/X! We would love to see what you're able to build using Zero-True. 