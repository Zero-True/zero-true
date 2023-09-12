def validate_color(value):
    """
    Validates the given color value.
    This validator ensures that the provided color is either one of the custom colors or follows the standard Material color palette format.
    """
    if value is None:
        return value
    custom_colors = ['primary','secondary', 'accent', 'error','info','success','warning']
    material_colors = ['red', 'pink', 'purple', 'deep-purple', 'indigo', 'blue', 'light-blue', 'cyan', 'teal', 'green', 'light-green', 'lime', 'yellow', 'amber', 'orange', 'deep-orange', 'brown', 'grey', 'blue-grey']
    if value in custom_colors:
        return value
    if '-' in value:
        color_name, shade = value.split('-')
        if color_name in material_colors and 100 <= int(shade) <= 900:
            return value
    raise ValueError(f"Invalid color value: '{value}'. Must be one of {custom_colors} or in the standard Material color palette format.")

def validate_min_less_than_max(max_value, values):
    """
    Validates that the maximum value is greater than the minimum value.
    """
    min_value = values.get('min')
    if min_value is not None and max_value <= min_value:
        raise ValueError(f"Max value '{max_value}' must be greater than min value '{min_value}'.")
    return max_value









