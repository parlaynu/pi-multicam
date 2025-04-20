import os
import re
import socket
import time
from ruamel.yaml import YAML
from jinja2 import Environment, BaseLoader, FileSystemLoader, select_autoescape


def _gethostname() -> str:
    """Return the first component of the current hostname"""
    return socket.gethostname().split('.')[0]


def _expand_vars(config_vars):
    """Iteratively expand configuration variables that reference other configuration variables"""
    p = re.compile(r'(.*?)\{\{(.*?)\}\}(.*)')
    found = True
    while found:
        found = False
        for k, v in config_vars.items():
            mo = p.match(v)
            if mo:
                found = True
                v2 = mo.group(1) + config_vars[mo.group(2).strip()] + mo.group(3)
                config_vars[k] = v2


def load(config_file: str, config_vars: dict) -> dict:
    """Load the specified configuration file.

    First, expand the contents as a jinja2 template, using the provided 'config_vars' dict
    to expand any template variables.
    
    The result should then be valid 'yaml' which is loaded and returned as a python dict.
    """    
    # load  the jinja2 templates
    if config_file == "-":
        # load from stdin
        env = Environment(loader=BaseLoader())
        template = env.from_string(sys.stdin.read())
    
    else:
        # load from a file
        config_file = os.path.abspath(os.path.expanduser(config_file))
        config_path = os.path.dirname(config_file)
        config_name = os.path.basename(config_file)
    
        env = Environment(
            loader=FileSystemLoader(config_path),
            autoescape=select_autoescape()
        )
        template = env.get_template(config_name)

    # add some 'standard' values to the vars if they aren't already there
    config_vars['hostname'] = config_vars.get('hostname', _gethostname())
    config_vars['timestamp'] = config_vars.get('timestamp', str(int(time.time())))
    _expand_vars(config_vars)

    # render the template with the provided configuration variables
    config_data = template.render(**config_vars)
    
    # parse the expanded template as YAML
    yaml = YAML(typ='safe')
    config = yaml.load(config_data)
    
    return config


def save(config: dict, save_dir: str, name: str) -> None:
    """Save the config dict to a file"""
    
    if not name.endswith('.yaml'):
        name += ".yaml"
    cfg_file = os.path.join(save_dir, name)

    with open(cfg_file, 'w') as f:
        yaml=YAML()
        yaml.dump(config, f)

