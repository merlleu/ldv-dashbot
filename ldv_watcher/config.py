from yaml import load, Loader

with open('config.yaml', 'r') as f:
    config = load(f, Loader=Loader)

import logging
logging.basicConfig(level=config['log_level'])