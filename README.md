<p align="center">
  <a href="https://zero-true.com/">
    <img src="https://github.com/HonkaDonka/zero-true/assets/30189257/9c96ddca-2201-4864-a726-4d4c2701b53e" width="300">
  </a>
</p>

<p align="center">
  <b>A New Way to Build and Collaborate on Data Apps</b>
</p>
  
<p align="center">
  <a href="https://docs.zero-true.com/" target="_blank"><strong>Documentation</strong></a> ·
  <a href="https://medium.com/zero-true" target="_blank"><strong>Blog</strong></a> ·
  <a href="" target="_blank"><strong>Discord</strong></a> <!-- Add Discord link or change -->
</p>

## What is Zero-True?

Zero-True is a Python and SQL reactive computational notebook able to create beautiful and 
professional data-driven applications. Designed to foster collaboration and improve data
accessibility, it offers a rich UI library and an intelligent code parser. Publish your 
apps with confidence and with ease. 

### Features

- **Integrated and Simple**: Python and SQL reactive computational notebook all in one. 
- **Transparent Updates**: No hidden state. Our reactive cell updates show you what your notebook looks like in real-time.
- **Dynamic and Interactive**: UI rendering with beautiful [Vuetify](https://vuetifyjs.com/en/) components, with customizable layouts.
- **Fast Prototyping**: Create rich, reactive apps with one click. 
- **Open-Source**: Join our community-driven project. 

## Quick Start

Make sure Python 3.9 is installed. (Anaconda or virtual environment recommended)

Open a terminal and run:

```bash
pip install zero-true
zero-true notebook
```

Once the application is running, head to http://localhost:1326 to begin creating your 
notebook!

### Quick Example

Create a new notebook and open a code cell with the following code:

```python
import zero_true as zt
slider = zt.Slider(id="slider_1")
zt.Text(id="text_1", text=str(slider.value) + " squared is " + str(slider.value**2))
```

Now run the cell and open your app!

<p align="center">
  <img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZjZwd3V4YTBuM3Z4dDA5cWk1MXp6N2lsZndieGIwMDloc2FjbzBzayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/KfXOJH8MwmDFa8ewEB/giphy.gif">
</p>

### More Complicated Example using Python + SQL 

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
