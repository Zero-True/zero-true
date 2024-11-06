from pydantic import Field, validator
from typing import Optional, Dict, Any
from io import BytesIO
import base64
from zt_backend.models.components.zt_component import ZTComponent
from zt_backend.models.state.user_state import UserContext

class FileInput(ZTComponent):
    """File input component allowing users to upload files."""

    component: str = Field(
        "v-file-input", description="Vue component name for file input"
    )
    value: Dict[str, str] = Field(
        {}, description="Dictionary of file name and file content"
    )
    accept: Optional[str] = Field(
        "*", description="Accepted file types (e.g., '.png, .jpg')"
    )
    placeholder: Optional[str] = Field(
        "Select file(s)", description="Placeholder text for file input"
    )
    label: Optional[str] = Field("", description="Label for the file input")
    multiple: Optional[bool] = Field(
        False, description="If true, allows multiple files"
    )
    show_size: Optional[bool] = Field(True, description="If true, shows file size")
    readonly: Optional[bool] = Field(
        False, description="If true, the input is read-only"
    )
    disabled: Optional[bool] = Field(
        False, description="If true, the input is disabled"
    )
    clearable: Optional[bool] = Field(
        True, description="If true, allows clearing of the input"
    )
    counter: Optional[bool] = Field(
        False, description="If true, shows a file count indicator"
    )

    @validator('value', always=True) #TODO: debug and replace with field validator
    def get_value_from_global_state(cls, value, values):
        id = values['id'] # Get the id if it exists in the field values
        execution_state = UserContext.get_state()
        try:
            if execution_state and id and id in execution_state.component_values:  # Check if id exists in global_state
                return execution_state.component_values[id]  # Return the value associated with id in global_state
        except Exception as e:
            e
        return value  # If id doesn't exist in global_state, return the original value

    def get_file(self, file_name: str = None):
        if file_name:
            file_content = self.value.get(file_name, None)
            if file_content:
                return BytesIO(base64.b64decode(file_content))
            return None
        else:
            first_file = next(iter(self.value.values()), None)
            if first_file:
                return BytesIO(base64.b64decode(file_content))
            return None

    def get_file_names(self):
        return list(self.value.keys())

    def get_files(self):
        files = []

        for file_name, file_content in self.value.items():
            files.append(BytesIO(base64.b64decode(file_content)))

        return files