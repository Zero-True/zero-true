from dataclasses import dataclass
from typing import Dict, List, Optional
import os
import re

@dataclass
class ComponentMetadata:
    name: str
    imports: List[str]
    props: Dict[str, str]
    example: str

class MdxComponentParser:
    def __init__(self, mdx_directory: str):
        self.mdx_directory = mdx_directory
        self._component_cache: Dict[str, ComponentMetadata] = {}

    def parse_mdx_file(self, component_name: str) -> Optional[ComponentMetadata]:
        """Parse MDX file and extract comprehensive component information."""
        if component_name in self._component_cache:
            return self._component_cache[component_name]

        filepath = os.path.join(self.mdx_directory, f"{component_name}.mdx")
        if not os.path.exists(filepath):
            return None

        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
            
            # Extract imports
            imports = self._extract_imports(content)
            
            # Extract props
            props = self._extract_props(content)
            
            # Extract minimal working example
            example = self._extract_minimal_example(content)

            metadata = ComponentMetadata(
                name=component_name,
                imports=imports,
                props=props,
                example=example
            )
            self._component_cache[component_name] = metadata
            return metadata

    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements from the content."""
        imports = []
        import_pattern = r'import\s+.*?from\s+[\'"].*?[\'"]'
        matches = re.finditer(import_pattern, content)
        return [match.group(0) for match in matches]

    def _extract_props(self, content: str) -> Dict[str, str]:
        """Extract component props and their types."""
        props = {}
        # Look for prop definitions in TypeScript/JSDoc style
        prop_pattern = r'@prop\s+{([^}]+)}\s+(\w+)'
        matches = re.finditer(prop_pattern, content)
        for match in matches:
            prop_type, prop_name = match.groups()
            props[prop_name] = prop_type.strip()
        return props

    def _extract_minimal_example(self, content: str) -> str:
        """Extract shortest complete example."""
        examples = re.findall(r'```python(.*?)```', content, re.DOTALL)
        if not examples:
            return ""
        return min((ex.strip() for ex in examples if 'zt.' in ex), key=len, default="")

    def get_components_context(self) -> str:
        """Generate strict context for code suggestions."""
        context_parts = [
            "### ZERO-TURE COMPONENT AUTOCOMPLETE CONTEXT ###",
            "STRICT RULES:",
            "1. ONLY suggest components that exist in documentation",
            "2. ALWAYS use zt. prefix for components",
            "3. NEVER create new component names",
            "4. EXACT MATCH REQUIRED for component names",
            "\nAVAILABLE COMPONENTS:"
        ]
        
        for filename in os.listdir(self.mdx_directory):
            if filename.endswith('.mdx'):
                component_name = filename[:-4]
                metadata = self.parse_mdx_file(component_name)
                if metadata:
                    context_parts.extend([
                        f"\nComponent: zt.{metadata.name}",
                        f"Usage: {metadata.example}",
                        "Props:",
                        *[f"  - {name}: {type_}" for name, type_ in metadata.props.items()],
                        "Imports:",
                        *[f"  {imp}" for imp in metadata.imports],
                        "-" * 50
                    ])

        return "\n".join(context_parts)

    def get_completion_hints(self) -> Dict[str, str]:
        """Generate completion hints for each component."""
        hints = {}
        for filename in os.listdir(self.mdx_directory):
            if filename.endswith('.mdx'):
                component_name = filename[:-4]
                metadata = self.parse_mdx_file(component_name)
                if metadata and metadata.example:
                    # Create completion hint with zt. prefix
                    hints[f"zt.{component_name}"] = metadata.example
        return hints