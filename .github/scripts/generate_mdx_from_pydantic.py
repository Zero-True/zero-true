import os
import zero_true
from pydantic import BaseModel, Field
from typing import Type


class ExampleModel(BaseModel):
    id: int = Field(..., description="The unique identifier for the example")
    name: str = Field(..., description="The name of the example")
    description: str = Field(..., description="A description of the example")


def generate_mdx(model: Type[BaseModel], file_path: str):
    """Generate an MDX file from a Pydantic model."""
    model_name = model.__name__
    properties = model.schema()["properties"]
    required = set(model.schema()["required"])

    mdx_content = f"""---
icon: "rectangle-code"
iconType: "solid"
---

<Card title="Example Usage" icon="code">
  ```python
import zero_true as zt

# Create a {model_name} component
sample_{model_name.lower()} = zt.{model_name}(
"""

    for field_name, field_info in properties.items():
        if field_name == "id":
            default = f" = 'sample_{model_name.lower()}'"
            mdx_content += (
                f"    {field_name}{default},  # {field_info['description']}\n"
            )
        elif field_name not in ["variable_name", "component", "triggerEvent"]:
            if field_info.get("type", "") == "string":
                default = (
                    f" = '{field_info.get('default')}'"
                    if "default" in field_info
                    else "''"
                )
            else:
                default = (
                    f" = {field_info.get('default')}"
                    if "default" in field_info
                    else "None"
                )

            mdx_content += (
                f"    {field_name}{default},  # {field_info['description']}\n"
            )

    mdx_content += f""")

```
</Card>

<Info>Below are the various attributes you can assign to the component. Utilizing them can allow for modifications to the pre-created object.</Info>

<ResponseField name="zero_true.{model_name}" type="Zero True Component">
  <Expandable title="properties">
   <AccordionGroup>
"""

    for field_name, field_info in properties.items():
        if field_name not in ["id", "variable_name", "component", "triggerEvent"]:
            mdx_content += f"""<Accordion title="{field_name}">
        **{field_name}:** {field_info.get('type', '')} = {field_info.get('default', 'None')}; 
        {field_info['description']}
</Accordion>
"""

    mdx_content += """
   </AccordionGroup>
  </Expandable>
</ResponseField>
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
