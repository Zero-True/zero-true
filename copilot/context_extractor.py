from dataclasses import dataclass
from typing import Dict, List, Optional
import os
import re

@dataclass
class ComponentProperty:
    name: str
    type: str
    description: str

@dataclass
class ComponentMetadata:
    name: str
    properties: List[ComponentProperty]
    example: str

class MdxComponentParser:
    def __init__(self, mdx_directory: str):
        self.mdx_directory = mdx_directory
        self._component_cache: Dict[str, ComponentMetadata] = {}

    def parse_mdx_file(self, filename: str) -> Optional[ComponentMetadata]:
        if filename in self._component_cache:
            return self._component_cache[filename]

        filepath = os.path.join(self.mdx_directory, filename)
        if not os.path.exists(filepath):
            return None

        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
            
            component_match = re.search(r'<ResponseField name="zero_true\.(\w+)"', content)
            if not component_match:
                return None
            component_name = component_match.group(1)
            
            properties = self._extract_properties(content)
            example = self._extract_complete_example(content, component_name)

            metadata = ComponentMetadata(
                name=component_name,
                properties=properties,
                example=example
            )
            self._component_cache[filename] = metadata
            return metadata

    def _extract_properties(self, content: str) -> List[ComponentProperty]:
        properties = []
        property_pattern = r'<Accordion title="([^"]+)">\s+\*\*([^:]+):\s*([^)]+)\*\*:\s*([^<]+)'
        matches = re.finditer(property_pattern, content, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            name, prop_name, type_str, description = match.groups()
            properties.append(ComponentProperty(
                name=name.strip(),
                type=type_str.strip(),
                description=description.strip()
            ))
        return properties

    def _extract_complete_example(self, content: str, component_name: str) -> str:
        """Extract complete example with all parameters but without comments."""
        example_match = re.search(r'```python(.*?)```', content, re.DOTALL)
        if not example_match:
            return ""

        example = example_match.group(1)
        
        component_pattern = rf'(\w+)\s*=\s*zt\.{component_name}\((.*?)\)'
        component_match = re.search(component_pattern, example, re.DOTALL)
        
        if not component_match:
            return ""
            
        var_name = component_match.group(1)
        params_block = component_match.group(2)

        params_list = []
        lines = params_block.split('\n')
        for line in lines:
            param_line = re.sub(r'#.*$', '', line).strip()
            if param_line:
                param_match = re.match(r'(\w+)\s*=\s*([^,]+)(?:,|$)', param_line)
                if param_match:
                    param_name, param_value = param_match.groups()
                    param_value = param_value.strip()
                    params_list.append(f"{param_name}={param_value}")

        clean_params = ','.join(params_list)
        clean_example = f"{var_name}=zt.{component_name}({clean_params})"
        
        return clean_example

    def generate_completion_context(self) -> str:
        """Generate minimal context with no extra spacing."""
        context_parts = [
        "/* COPILOT RULES",
        "- Only use components listed below - no custom components",
        "- No empty lines in suggestions",
        "- No indentation",
        "- No alignment formatting",
        "- Minimal spaces between parameters",
        "- Don't Create own parameters for component only show if present in usage"
        "*/",
        ]
        
        # Component definitions
        context_parts.append("\n/* Component definitions and their common usage:")
        for filename in os.listdir(self.mdx_directory):
            if filename.endswith('.mdx'):
                metadata = self.parse_mdx_file(filename)
                if metadata:
                    example = metadata.example if metadata.example else f"sample_{metadata.name.lower()}=zt.{metadata.name}(id='sample_{metadata.name.lower()}')"
                    context_parts.append(f"Component: {metadata.name}")
                    context_parts.append(f"Usage: {example}")
                    
        context_parts.append("*/")
        return '\n'.join(context_parts)