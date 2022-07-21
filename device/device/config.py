"""
Config Loader

Loads config.ini and selects the current config based on the DEVICE_ENV
environment variable.
"""
from os import environ
from pathlib import Path
from configparser import ConfigParser

ENV = environ.get('DEVICE_ENV')
configFile = Path(Path(__file__).resolve().parent.parent, 'config.ini')
config = ConfigParser()
config.read(configFile)
config.sections()

if ENV:
    if ENV in config:
        CONFIG = config[ENV]
    else:
        raise EnvironmentError(
            f"Environment '{ENV}' does not exist within config")
else:
    CONFIG = config['DEFAULT']
