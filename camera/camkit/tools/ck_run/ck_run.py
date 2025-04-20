"""Builds the objects in a configuration file and runs the main pipeline."""
import argparse
import os

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
        'output_dir': os.path.join(args.output, '{{ timestamp }}')
    }

    # update config any overrides provided on the command line
    for override in args.overrides:
        key, value = override.split('=', 1)
        config_vars[key] = value
    
    # load the config file
    print("Loading config", flush=True)
    cfg = config.load(args.config, config_vars)
    
    # save the config file into the output dir
    os.makedirs(config_vars['output_dir'], exist_ok=True)
    config.save(cfg, config_vars['output_dir'], 'config')
        
    # build the configured system
    print("Building config", flush=True)
    built = config.build(cfg)

    # run the pipeline
    print("Running")
    if pipe := built.get('pipeline', None):
        for idx, item in enumerate(pipe):
            if args.verbose:
                idx = int(item.get('idx', idx))
                print(f"Item {idx:04d}")
            pass

