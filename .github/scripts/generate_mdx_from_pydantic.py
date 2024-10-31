import os
import zero_true
from pydantic import BaseModel, Field
from typing import Type


plotly_example = """
   </AccordionGroup>
  </Expandable>
</ResponseField>

<Card title="Example Usage" icon="code">
  ```python
import zero_true as zt
import pandas as pd
import plotly.express as px

# Some sample data pulled from Wikipedia
table_MN = pd.read_html('https://en.wikipedia.org/wiki/Minnesota')
example_data = table_MN[6]
example_data['Country'] = example_data['Country'].str.replace(r"\[.*\]", "", regex=True)

fig = px.bar(example_data, x='Country', y='Population')
zt.plotlyComponent(id='plot', figure=fig)
```
</Card>
<Card title="Example Output">
<Frame>
  <img src="/images/plotly_example.png" />
</Frame>
</Card>
"""

matplotlib_example = """
   </AccordionGroup>
  </Expandable>
</ResponseField>

<Card title="Example Usage" icon="code">
  ```python
import zero_true as zt
import pandas as pd
import matplotlib.pyplot as plt

# Some sample data pulled from Wikipedia
table_MN = pd.read_html('https://en.wikipedia.org/wiki/Minnesota')
example_data = table_MN[6]
example_data['Country'] = example_data['Country'].str.replace(r"\[.*\]", "", regex=True)

plt.clf()
plt.bar(example_data["Country"], example_data["Population"])
plt.xlabel("Country")
plt.ylabel("Values")
plt.xticks(rotation=90)
plt.subplots_adjust(bottom=0.3)

zt.matplotlib(id='plot', figure=plt.gcf(), width=200, height=600)
```
</Card>
<Card title="Example Output">
<Frame>
  <img src="/images/matplotlib_example.png" />
</Frame>
</Card>
"""

dataframe_example = """
   </AccordionGroup>
  </Expandable>
</ResponseField>

<Card title="Example Usage" icon="code">
  ```python
import zero_true as zt
import pandas as pd

# Some sample data pulled from Wikipedia
table_MN = pd.read_html('https://en.wikipedia.org/wiki/Minnesota')
example_data = table_MN[6]
example_data['Country'] = example_data['Country'].str.replace(r"\[.*\]", "", regex=True)

zt.dataframe(id="example_df", df=example_data)
```
</Card>
<Card title="Example Output">
<Frame>
  <img src="/images/dataframe_example.png" />
</Frame>
</Card>
"""

def type_swap(type_string: str):
    if type_string == "number":
        return "float"
    elif type_string == "array":
        return "list"
    else:
        return type_string


def generate_mdx(model: Type[BaseModel], file_path: str):
    """Generate an MDX file from a Pydantic model."""
    model_name = model.__name__
    properties = model.model_json_schema()["properties"]

    mdx_content = f"""---
icon: "rectangle-code"
iconType: "solid"
---

<Info>Below are the various attributes you can assign to the component. Utilizing them can allow for modifications to the pre-created object.</Info>

<ResponseField name="zero_true.{model_name}" type="Zero True Component">
  <Expandable title="properties">
   <AccordionGroup>
"""
    for field_name, field_info in properties.items():
        if not field_info.get("type", None):
            type_string = " | ".join(
                [
                    type_swap(field_type.get("type", ""))
                    for field_type in field_info.get("anyOf", [])
                    if field_type.get("type", "") != "null"
                ]
            )
        else:
            type_string = type_swap(field_info.get("type", ""))
        if field_name not in ["variable_name", "component", "triggerEvent"]:
            mdx_content += f"""<Accordion title="{field_name}">
        **{field_name} ({type_string}):** {field_info['description']}
</Accordion>
"""
    if model_name == "Matplotlib":
        mdx_content += matplotlib_example
    elif model_name == "PlotlyComponent":
        mdx_content += plotly_example
    elif model_name == "DataFrame":
        mdx_content += dataframe_example
    else:
        mdx_content += f"""
   </AccordionGroup>
  </Expandable>
</ResponseField>

<Card title="Example Usage" icon="code">
  ```python
import zero_true as zt

sample_{model_name.lower()} = zt.{model_name}(
"""

        for field_name, field_info in properties.items():
            if field_name == "id":
                default = f" = 'sample_{model_name.lower()}'"
                mdx_content += (
                    f"    {field_name}{default},  # {field_info['description']}\n"
                )
            elif field_name not in ["variable_name", "component", "triggerEvent"]:
                if field_info.get("type", "") == "string" or (
                    (
                        field_type.get("type", "") == "string"
                        for field_type in field_info.get("anyOf", [])
                    )
                    and isinstance(field_info.get("default", ""), str)
                ):
                    default = (
                        f" = '{field_info.get('default')}'"
                        if "default" in field_info
                        else " = ''"
                    )
                else:
                    default = (
                        f" = {field_info.get('default')}"
                        if "default" in field_info
                        else " = None"
                    )

                mdx_content += (
                    f"    {field_name}{default},  # {field_info['description']}\n"
                )

        mdx_content += f""")

```
</Card>
"""

    # <Card title="Example Output" icon="computer">

    # <iframe src="https://published.zero-true.com/srrey/examplebutton/" width="100%" height="300"></iframe>

    # </Card>

    with open(file_path, "w") as file:
        file.write(mdx_content)


if __name__ == "__main__":
    output_dir = "mintlify-docs/Components"
    generate_mdx(zero_true.Slider, os.path.join(output_dir, "Slider.mdx"))
    generate_mdx(zero_true.Button, os.path.join(output_dir, "Button.mdx"))
    generate_mdx(zero_true.Rating, os.path.join(output_dir, "Rating.mdx"))
    generate_mdx(zero_true.TextInput, os.path.join(output_dir, "TextInput.mdx"))
    generate_mdx(zero_true.FileInput, os.path.join(output_dir, "FileInput.mdx"))
    generate_mdx(zero_true.TextArea, os.path.join(output_dir, "TextArea.mdx"))
    generate_mdx(zero_true.RangeSlider, os.path.join(output_dir, "RangeSlider.mdx"))
    generate_mdx(zero_true.SelectBox, os.path.join(output_dir, "SelectBox.mdx"))
    generate_mdx(zero_true.NumberInput, os.path.join(output_dir, "NumberInput.mdx"))
    generate_mdx(zero_true.Image, os.path.join(output_dir, "Image.mdx"))
    generate_mdx(zero_true.Text, os.path.join(output_dir, "Text.mdx"))
    generate_mdx(zero_true.DataFrame, os.path.join(output_dir, "DataFrame.mdx"))
    generate_mdx(zero_true.Matplotlib, os.path.join(output_dir, "Matplotlib.mdx"))
    generate_mdx(
        zero_true.PlotlyComponent, os.path.join(output_dir, "PlotlyComponent.mdx")
    )
    generate_mdx(zero_true.Autocomplete, os.path.join(output_dir, "Autocomplete.mdx"))
    generate_mdx(zero_true.Card, os.path.join(output_dir, "Card.mdx"))
    generate_mdx(zero_true.Timer, os.path.join(output_dir, "Timer.mdx"))
    generate_mdx(zero_true.iFrame, os.path.join(output_dir, "iFrame.mdx"))
    generate_mdx(zero_true.HTML, os.path.join(output_dir, "HTML.mdx"))
