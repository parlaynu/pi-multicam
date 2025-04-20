"""The core generator operations that can be chained together to build processing pipelines."""


def get_nested_value(item, keys):
    if isinstance(keys, str):
        keys = keys.split('.')

    nested = item
    for key in keys:
        nested = nested[key]

    return nested


def set_nested_value(item, keys, value):
    if isinstance(keys, str):
        keys = keys.split('.')
    
    nested = item
    for key in keys[:-1]:
        if key not in nested:
            nested[key] = {}
        nested = nested[key]
    
    nested[keys[-1]] = value

