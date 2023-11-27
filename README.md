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

- 📝 Python + SQL reactive computational notebook.
- 🌌 No hidden state. Our reactive cell updates show you what your notebook looks like in real time.
- 📊 Dynamic UI rendering with beautiful [Vuetify](https://vuetifyjs.com/en/) components.
- 🔄 Automatic dependency tracking between cells.
- 🚀 Integrated app publishing with a simple command.

## ⚙ Requirements

- Python 3.9 (Anaconda or virtual environment recommended)

## 🚀 Quick Start

```bash
pip install zero-true
zero-true notebook
```

### Usage

Once the application is running, navigate to http://localhost:1326 and start creating and executing code cells. Click the "Run" button to execute code and visualize the output below the editor.

#### Basic Example

```python
import zero_true as zt
slider = zt.Slider(id='slider_1')
print('The squared value is '+str(slider.value**2))
```


#### More Complicated Example using Python + SQL 

For this example you will need scikitlearn 

```bash
pip install scikit-learn
```

Once it has installed, launch your notebook. We will be using the Iris dataset from scikit learn to create an app where people 
can filter the data using the our UI components and SQL editor. We start with a Python cell:

```python

import zero_true as zt
import sklearn
import pandas as pd
from sklearn import datasets
iris = datasets.load_iris()
# Creating a DataFrame with the feature data
iris_df = pd.DataFrame(data=iris.data, columns=iris.feature_names)
# Map the target indices to target names
iris_df['target'] = iris.target
iris_df['target_name'] = iris_df['target'].apply(lambda x: iris.target_names[x])
# Rename columns to remove spaces and standardize
iris_df.columns = [col.replace(' ', '_').replace('(cm)', 'cm') for col in iris_df.columns]
iris_df.columns = [ col.replace(' ','_').replace('(cm)','cm') for col in iris_df.columns]
iris_df.drop('target',axis=1,inplace = True)
#all the different sliders
sepal_width_slider  = zt.RangeSlider(id = 'sepal_width',
                                     min = iris_df.sepal_width_cm.min(),
                                     max = iris_df.sepal_width_cm.max(),
                                     step = 0.1,label = 'Sepal Width')
petal_width_slider  = zt.RangeSlider(id = 'petal_width',
                                     min = iris_df.petal_width_cm.min(),
                                     max = iris_df.petal_width_cm.max(),
                                     step = 0.1,label = 'Petal Width')
sepal_length_slider = zt.RangeSlider(id = 'sepal_length',
                                     min = iris_df.sepal_length_cm.min(),
                                     max = iris_df.sepal_length_cm.max(),
                                     step = 0.1, label = 'Sepal Length')
petal_length_slider = zt.RangeSlider(id = 'petal_lenght',
                                     min = iris_df.petal_length_cm.min(),
                                     max = iris_df.petal_length_cm.max(),
                                     step = 0.1, label = 'Petal Length')
```

Then add a SQL cell below to query the dataframe. Notice how we can query a pandas dataframe directly and reference our
UI components in the query:

```sql
SELECT * FROM iris_df
WHERE (sepal_length_cm BETWEEN {sepal_length_slider.value[0]} AND {sepal_length_slider.value[1]})
AND  (sepal_width_cm BETWEEN {sepal_width_slider.value[0]} AND {sepal_width_slider.value[1]})
AND  (petal_width_cm BETWEEN {petal_width_slider.value[0]} AND {petal_width_slider.value[1]})
AND (petal_length_cm BETWEEN {petal_length_slider.value[0]} AND {petal_length_slider.value[1]})
```

Notice how dragging the slider will update the dataframe. Set the parameters for your Iris bouquet and check out the data! You can 
see a published app for this [example](https://published.zero-true-cloud.com/examples/iris/).

![More Complicated Example](/docs/assets/example_gif.gif)

We support a large range of use cases and UI components. For more information please check out our docs: [docs](https://docs.zero-true.com/)! You can also find some more narrative tutorials at our Medium publication [here](https://medium.com/zero-true). 

### Publishing 

Publishing your notebook is easy. Currently it's a one liner from the command line:


```bash
zero-true publish [api-key] [user-name] [project-name] [project-source]
```
Publishing is only open to a limited audience. If you are interested in publishing your notebook at a URL in our public cloud please fill out the email waiting list on our [website](https://zero-true.com/).

### Community

Reach out on GitHub with any feature requests or bugs that you encounter and share your work with us on [Twitter/X](https://twitter.com/ZeroTrueML)! We are also active on [linkedin](https://www.linkedin.com/company/zero-true). We would love to see what you're able to build using Zero-True. 