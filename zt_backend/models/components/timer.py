from pydantic import Field, validator
from zt_backend.models.components.zt_component import ZTComponent
from zt_backend.models.state.user_state import UserContext

class Timer(ZTComponent):
    """Timer is a component that allows for execution of code at a set interval. This does not have any visual output"""
    component: str = Field("v-timer", description="Vue component name")
    interval: int = Field(100000, description="Interval in milliseconds")
    value: bool = Field(False, description="Flag for execution under interval")
    triggerEvent: str = Field('click',description="Trigger event for when to execute a run")
        
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