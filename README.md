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
  <a href="https://discord.gg/YDFeP9hFte" target="_blank"><strong>Discord</strong></a> <!-- Add Discord link or change -->
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
- **Open-Source**: Join our community-driven project and contribute to Zero-True's future.

## Quick Start

Make sure Python 3.8+ is installed. (Anaconda or virtual environment recommended)

Open a terminal and run:

```bash
# install the packages
pip install zero-true
# run your first notebook
zero-true notebook
```

Once the application is running, head to http://localhost:1326 to begin editing your 
notebook!

### Quick Example

Open a new notebook and create a code cell with the following code:

```python
import zero_true as zt
slider = zt.Slider(id="slider_1")
print(str(slider.value) + " squared is " + str(slider.value**2))
```

Now run the cell and open your app!

<p align="center">
  <img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMnpvbmRwZXh3YXcwMml1YjgxMm05bXc0MDVlMWZ3NWVzZGJ3bnNudyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/a6xAYpoHEVqHqoJlsp/giphy.gif">
</p>

### What Else?

Zero-True comes with a variety of features designed to streamline your experience. Some examples include: 

<table border="0">
  <tr>
    <td>UI Components</td>
    <td>Different Cell Types</td>
    <td>Plotly Charts</td>
  </tr>
  <tr>
    <td>
      <a target="_blank" href="https://docs.zero-true.com/ui_components/index.html">
        <img src="https://github.com/HonkaDonka/zero-true/assets/30189257/d72da346-6310-4d36-ac02-4dcb72b76547" style="max-height:150px; width:auto; display:block;">
      </a>
    </td>
    <td>
      <a target="_blank" href="https://docs.zero-true.com/cell_types.html">
        <img src="https://github.com/HonkaDonka/zero-true/assets/30189257/ae6c311b-5d1d-4efe-968a-a1e398a17d7e" style="max-height:150px; width:auto; display:block;">
      </a>
    </td>
    <td>
      <a target="_blank" href="https://docs.zero-true.com/ui_components/plotly.html">
        <img src="https://github.com/HonkaDonka/zero-true/assets/30189257/e456c9ca-bd61-4284-a3f7-cef2b84007a2" style="max-height:150px; width:auto; display:block;">
      </a>
    </td>
  </tr>
</table>

Check out our docs for more info!

### Publishing Your Notebook


From the command line, run: 

```bash
# publish your notebook
zero-true publish [api-key] [user-name] [project-name] [project-source]
```

**Note:** Publishing is currently only open to a limited audience. 

If you are interested in publishing your notebook at a URL in our public cloud, please fill out the email waiting list on our [website](https://zero-true.com/).

## Resources

### Documentation & Examples
- Check out our [docs](https://docs.zero-true.com/index.html) to learn more about Zero-True.
- Read our [blog](https://medium.com/zero-true) for examples from creators.
### Community
- Connect with others at our [discord](https://discord.gg/YDFeP9hFte).
- [Star/Follow](https://github.com/Zero-True) us on GitHub.
- Join the [waitlist](https://zero-true.com/) for our cloud.
- Share your work with us on [Twitter/X](https://twitter.com/ZeroTrueML).
- Check out our [Linkedin](https://www.linkedin.com/company/zero-true).

**We would love to see what you're able to build using Zero-True!**
