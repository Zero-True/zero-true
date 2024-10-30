from pydantic import Field, validator
from typing import Optional, List
from zt_backend.models.components.zt_component import ZTComponent
from zt_backend.models.state.user_state import UserContext

class FileInput(ZTComponent):
    """File input component allowing users to upload files."""
    
    component: str = Field("v-file-input", description="Vue component name for file input")
    value: Optional[List[str]] = Field(default_factory=list, description="List of uploaded file names")
    accept: Optional[str] = Field("*", description="Accepted file types (e.g., '.png, .jpg')")
    placeholder: Optional[str] = Field("Select file(s)", description="Placeholder text for file input")
    label: Optional[str] = Field("", description="Label for the file input")
    multiple: Optional[bool] = Field(False, description="If true, allows multiple files")
    show_size: Optional[bool] = Field(True, description="If true, shows file size")
    readonly: Optional[bool] = Field(False, description="If true, the input is read-only")
    disabled: Optional[bool] = Field(False, description="If true, the input is disabled")
    clearable: Optional[bool] = Field(True, description="If true, allows clearing of the input")
    counter: Optional[bool] = Field(False, description="If true, shows a file count indicator")
    triggerEvent: str = Field(
        None, description="Trigger event to send code to the backend"
    )

    @validator("value", always=True)
    def get_value_from_global_state(cls, value, values):
        id = values.get("id")
        execution_state = UserContext.get_state()
        try:
            if execution_state and id and id in execution_state.component_values:
                return execution_state.component_values[id]
        except Exception as e:
            print(f"Error accessing state: {e}")
        return value
