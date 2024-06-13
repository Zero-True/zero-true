from pydantic import Field, validator, constr, field_validator
from pydantic.types import Literal
from zt_backend.models.components.zt_component import ZTComponent
from zt_backend.models.state.user_state import UserContext
from typing import List, Optional, Union
from datetime import datetime, date


type_str = "date"
month_var = "month"

'''
today_date = datetime.today().date().isoformat()
today_date_obj = datetime.strptime(today_date, "%Y-%m-%d").date()
# Get the current date and time
now = datetime.now()

# Extract the current month and year
current_month = now.month - 1 # 0-12 for months
current_year = now.year

print(today_date)
print(type(today_date))
print(type(today_date_obj))
'''


class DatePicker(ZTComponent):
    """Date Picker component allows a user to select a date"""
    component: str = Field("v-date-picker", description="Vue component name")
    hide_weekdays: Optional[bool] = Field(False, description="Hide the days of the week letters in the calendar view")
    landscape: Optional[bool] = Field(False, description="Puts the Date Picker component into landscape mode.")
    next_icon: str = Field('$next', description="Sets the icon for next month/year button in the Date Picker Component")
    prev_icon: str = Field('$prev', description="Sets the icon for prev month/year button in the Date Picker Component") 
    view_mode: Literal[f'{month_var}', 'months', 'year'] = Field('month', description="Determines which picker is being displayed. Allowed values: 'month', 'months', 'year'")
    weekdays: Optional[List[int]] = Field([0, 1, 2, 3, 4, 5, 6], description="An array of weekdays to display")
    disabled: Optional[bool] = Field(False, description="Determines if the Date Picker component is disabled")
    color: Optional[str] = Field('primary', pre=True, description="Color of the Calendar. Can be custom or standard Material color")
    width: Optional[int] = Field(100, description="Width of the Date Picker component")
    height: Optional[int] = Field(100, description="Height of the Date Picker component")
    triggerEvent: str = Field('update:modelValue', description="Trigger event for when to run based on the selected value")

    '''
    type: Literal[f'{type_str}'] = Field('date', description="Type of the value in date picker")  # Non-editable field
    # value: datetime = Field(datetime.today().date().isoformat(), description="Selected date value")
    value: str = Field(today_date, description="Selected date value")
    month: Union[int, str] = Field(f'{current_month}', description="The current month number to show in the Date picker view")#change
    year: int = Field(current_year, description="The current year number to show")
    '''

    '''
    @validator('weekdays', always=True)
    def validate_weekdays(cls, v):
        if all(isinstance(day, int) and 0 <= day <= 6 for day in v):
            return v
        else:
            raise ValueError("All items in weekdays must be integers between 0 and 6 inclusive")
    
    @field_validator('value', mode="before")
    def validate_iso_date(cls, v):
        if v is None:
            return v
        return validate_iso_date_format(v)
    
    @validator('value', always=True)
    def get_value_from_global_state(cls, value, values):
        id = values.get('id')  # Get the id if it exists in the field values
        execution_state = UserContext.get_state()
        try:
            if execution_state and id and id in execution_state.component_values:  # Check if id exists in global_state
                return execution_state.component_values[id]  # Return the value associated with id in global_state
        except Exception as e:
            e
        return value  # If id doesn't exist in global_state, return the original value
    '''

