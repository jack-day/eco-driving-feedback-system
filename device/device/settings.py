"""
Device Settings

Reads and modifies the device's settings stored in settings.yaml
"""
from pathlib import Path
import yaml
from config import CONFIG

filename = Path(Path(__file__).resolve().parent.parent, CONFIG['settingsFile'])

with open(filename, 'r') as file:
    SETTINGS = yaml.safe_load(file)
