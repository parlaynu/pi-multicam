import copy
import importlib


def build(config: dict) -> dict:
    """Process a configuration dict and create objects and make connections.

    Recognises the following special keys in the dict:
    
        __target__   : the value is a python object to construct, passing any remaining
                       key/value pairs to the object's constructor.
        __instance__ : the value is the name of an existing object that is looked up 
                       and replaced as the value
        __enum__     : the value is the name of an enum that is used to replace the value.
        pipeline*    : any top level key that starts with pipeline, is built in a special
                       way with each object receiving a reference to the previous object
                       in its constructor.
    """    
    config = copy.deepcopy(config)
    instances = {}
    if isinstance(config, (list, tuple)):
        return _build_list(config, instances)
    else:
        return _build_dict("root", config, instances)


def _build_dict(key: str, config: dict, instances: dict):
    # build nested objects first
    for k, v in config.items():
        if k.startswith('pipeline'):
            subkey = k if key == "root" else None
            config[k] = _build_pipeline(subkey, v, instances)
        elif isinstance(v, (list, tuple)):
            config[k] = _build_list(v, instances)
        elif isinstance(v, dict):
            subkey = k if key == "root" else None
            config[k] = _build_dict(subkey, v, instances)
    
    # if the __instance__ key exists, get the value from the instances
    #   dictionary
    if iname := config.get('__instance__', None):
        instance = instances[iname]
        if isinstance(instance, list):
            return instance.pop()
        else:
            return instance
    
    # if the __target__ key exists, instantiate the object...
    if enum := config.get('__enum__', None):
        return _build_enum(enum, config)

    # if the __target__ key exists, instantiate the object...
    if target := config.get('__target__', None):
        target = _build_target(target, config)
        if key:
            instances[key] = target
        return target

    # nothing else to do... return the config
    return config

    
def _build_list(config: list, instances: dict):
    for idx, v in enumerate(config):
        if isinstance(v, (list, tuple)):
            config[idx] = _build_list(v, instances)
        elif isinstance(v, dict):
            config[idx] = _build_dict(None, v, instances)
            
    return config


def _build_enum(target: str, config: dict):
    del config['__enum__']

    tgt_class_path = target.split('.')
    tgt_enum_name = tgt_class_path[-1]
    tgt_class_name = tgt_class_path[-2]
    tgt_module_path = '.'.join(tgt_class_path[0:-2])
    
    tgt_module = importlib.import_module(tgt_module_path)
    tgt_class = getattr(tgt_module, tgt_class_name)
    
    return getattr(tgt_class, tgt_enum_name)


def _build_target(target: str, config: dict):
    del config['__target__']
    
    tgt_class_path = target.split('.')
    tgt_class_name = tgt_class_path[-1]
    tgt_module_path = '.'.join(tgt_class_path[0:-1])
    
    tgt_module = importlib.import_module(tgt_module_path)
    tgt_class = getattr(tgt_module, tgt_class_name)

    return tgt_class(**config)


def _build_pipeline(key: str, config: dict, instances: dict):
    pipe = None
    for idx, v in enumerate(config):
        if pipe is not None and v.get('pipe', None) is None:
            v['pipe'] = pipe
        config[idx] = pipe = _build_dict(None, v, instances)
    
    if key:
        instances[key] = pipe

    return pipe

