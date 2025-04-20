"""Helper functions to bypass requirements for json serialization."""
import types


def stringify_list(items: list) -> list:
    newitems = []
    for v in items:
        if type(v).__module__ != "builtins":
            newitems.append(str(type(v)))
        elif isinstance(v, types.GeneratorType):
            newitems.append(str(v))
        elif isinstance(v, (list, tuple)):
            newitems.append(stringify_list(v))
        elif isinstance(v, dict):
            newitems.append(stringify_dict(v))
        else:
            newitems.append(v)

    return newitems


def stringify_dict(items: dict) -> dict:
    newitems = {}
    for k, v in items.items():
        if type(v).__module__ != "builtins":
            newitems[k] = str(type(v))
        elif isinstance(v, types.GeneratorType):
            newitems[k] = (str(v))
        elif isinstance(v, (list, tuple)):
            newitems[k] = stringify_list(v)
        elif isinstance(v, dict):
            newitems[k] = stringify_dict(v)
        else:
            newitems[k] = v

    return newitems

