import os
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
        default = f" = {field_info.get('default')}" if "default" in field_info else ""
        mdx_content += f"    {field_name}={default},  # {field_info['description']}\n"

    mdx_content += """)

# Assuming you have a mechanism to render or use this component within a layout
layout = zt.Layout(components=[sample_{model_name.lower()}])

```
</Card>

<Card title="Example Output" icon="computer">

<iframe src="https://published.zero-true.com/srrey/examplebutton/" width="100%" height="300"></iframe>

</Card>

## Overview

`pydantic model zero_true.{model_name}` 

The {model_name} component is a fundamental element in user interfaces, offering a simple yet versatile method for user interaction. This standard component can be customized with different attributes to match the design requirements of any application. 

<Note> It supports enabling or disabling based on application logic, and its functionality extends to capturing interactions through event triggers that can be connected to backend processes. The straightforward implementation makes it an essential tool for initiating actions, submitting forms, or triggering events within a UI.</Note>


## JSON Schema

<Accordion title="Field Definitions"> 
```json
{{
   "title": "{model_name}",
   "description": "{model.schema().get('description', '')}",
   "type": "object",
   "properties": {properties},
   "required": {list(required)}
}}
```
</Accordion> 

<Info>Below are the various attributes you can assign to the component. Utilizing them can allow for modifications to the pre-created object.</Info>

<ResponseField name="zero_true.{model_name}" type="Zero True Component">
  <Expandable title="properties">
   <AccordionGroup>
"""

    for field_name, field_info in properties.items():
        mdx_content += f"""<Accordion title="field {field_name}">
      **field {field_name}:** {field_info['type']} = {field_info.get('default', 'None')}; 
      {field_info['description']}
</Accordion>
"""

    mdx_content += """
   </AccordionGroup>
  </Expandable>
</ResponseField>

<Card title="Methods">
  classmethod *get_value_from_global_state*(value, values)
</Card>
"""

    with open(file_path, 'w') as file:
        file.write(mdx_content)

if __name__ == "__main__":
    output_dir = 'docs'
    os.makedirs(output_dir, exist_ok=True)
    generate_mdx(ExampleModel, os.path.join(output_dir, 'example_model.mdx'))
```
