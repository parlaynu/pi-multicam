"""Builds the objects in a configuration file and runs the main pipeline."""
import argparse
import os, sys
from ruamel.yaml import YAML

import camkit.config as config


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', help='verbose output', action='store_true')
    parser.add_argument('-o', '--output', help='the root of the output directory', type=str, default='local')
    parser.add_argument('config', help='the configuration file to load', type=str)
    parser.add_argument('overrides', help='key=value configuration overrides', nargs='*', type=str)
    args = parser.parse_args()

    # config defaults
    config_vars = {
        'output_dir': os.path.join(args.output, '{{ timestamp }}'),
    }

    # update config any overrides provided on the command line
    for override in args.overrides:
        key, value = override.split('=', 1)
        config_vars[key] = value
    
    # load the config file
    cfg = config.load(args.config, config_vars)

    # output to stdout    
    yaml=YAML()
    yaml.dump(cfg, sys.stdout)
