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

slider = zt.Slider(id='slider',row=0,column=0,label='First Slider')

if slider.value < 50:
    color = 'primary'
else:
    color = 'accent'
    
slider1 = zt.RangeSlider(id='slider1',color=color,row=0,column=0, label= 'Second Slider')
slider2 = zt.Slider(id='slider3',color=color,row=2,column=0,label='Third Slider')
slider4 = zt.Slider(id='slider4',label = 'Fourth Slider')

button = zt.Button(id='btn',text ='Only Button')

```

And the resulting layout:

![More Complicated Example](/docs/assets/example_layout.png)


For more information checkout our [docs](https://docs.zero-true.com/)!


### Community

Reach out on GitHub with any feature requests or bugs that you encounter and share your work with us on Twitter/X! We would love to see what you're able to build using Zero-True. 