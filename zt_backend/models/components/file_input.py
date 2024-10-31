from pydantic import Field
from typing import Optional
from zt_backend.models.components.zt_component import ZTComponent

class FileInput(ZTComponent):
    """File input component allowing users to upload files."""
    
    component: str = Field("v-file-input", description="Vue component name for file input")
    accept: Optional[str] = Field("*", description="Accepted file types (e.g., '.png, .jpg')")
    placeholder: Optional[str] = Field("Select file(s)", description="Placeholder text for file input")
    label: Optional[str] = Field("", description="Label for the file input")
    multiple: Optional[bool] = Field(False, description="If true, allows multiple files")
    show_size: Optional[bool] = Field(True, description="If true, shows file size")
    readonly: Optional[bool] = Field(False, description="If true, the input is read-only")
    disabled: Optional[bool] = Field(False, description="If true, the input is disabled")
    clearable: Optional[bool] = Field(True, description="If true, allows clearing of the input")
    counter: Optional[bool] = Field(False, description="If true, shows a file count indicator")