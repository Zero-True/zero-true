from pydantic import Field
from typing import List, Optional
from zt_backend.models.components.zt_component import ZTComponent

class FileUploader(ZTComponent):
    component: str = Field("v-file-input", description="Vue component name")
    filename: Optional[List[str]] = Field([], description="List of file paths")
    value: str = Field("", description="The input file value")