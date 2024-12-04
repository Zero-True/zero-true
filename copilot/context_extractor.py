import os
import re
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ComponentMetadata:
    name: str
    description: str
    props: Dict[str, Dict[str, str]]
    example: str

class MdxComponentParser:
    def __init__(self, mdx_directory: str):
        self.mdx_directory = mdx_directory
        self._component_cache: Dict[str, ComponentMetadata] = {}

    def parse_mdx_file(self, component_name: str) -> Optional[ComponentMetadata]:
        """Parse MDX file and extract essential component information."""
        if component_name in self._component_cache:
            return self._component_cache[component_name]

        filepath = os.path.join(self.mdx_directory, f"{component_name}.mdx")
        if not os.path.exists(filepath):
            return None

        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()

            # Extract component description
            description = self._extract_description(content)
            
            # Extract only required props
            props = self._extract_required_props(content)
            
            # Extract minimal working example
            example = self._extract_minimal_example(content)

            metadata = ComponentMetadata(
                name=component_name,
                description=description,
                props=props,
                example=example
            )
            self._component_cache[component_name] = metadata
            return metadata

    def _extract_description(self, content: str) -> str:
        """Extract first paragraph as component description."""
        match = re.search(r'^([^#\n].*?)(?=\n\n|\Z)', content, re.MULTILINE | re.DOTALL)
        return match.group(1).strip() if match else ""

    def _extract_required_props(self, content: str) -> Dict[str, Dict[str, str]]:
        """Extract only required properties."""
        props = {}
        matches = re.finditer(
            r'<Accordion title="([^"]+)">\s*\*\*([^*]+)\*\*:([^<]+)',
            content
        )
        for match in matches:
            name, type_info, desc = match.groups()
            if "required" in desc.lower():
                props[name] = {
                    'type': type_info.strip(),
                    'description': desc.strip()
                }
        return props

    def _extract_minimal_example(self, content: str) -> str:
        """Extract shortest complete example."""
        examples = re.findall(r'```python(.*?)```', content, re.DOTALL)
        if not examples:
            return ""
        # Return shortest valid example
        return min((ex.strip() for ex in examples if 'import' in ex), 
                  key=len, default="")

    def get_components_context(self) -> str:
        """Generate optimized context for code suggestions."""
        context_parts = []
        
        for filename in os.listdir(self.mdx_directory):
            if filename.endswith('.mdx'):
                component_name = filename[:-4]
                metadata = self.parse_mdx_file(component_name)
                
                if metadata and metadata.example:
                    context = [
                        f"# {metadata.name} Component",
                        f"# {metadata.description}",
                    ]
                    
                    if metadata.props:
                        context.append("# Required props:")
                        for prop, details in metadata.props.items():
                            context.append(f"#   {prop}: {details['type']}")
                    
                    context.append("# Usage example:")
                    context.append(metadata.example)
                    context_parts.append("\n".join(context))

        return "\n\n".join(context_parts)