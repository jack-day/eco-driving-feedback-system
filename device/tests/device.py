"""Adds the device source code folder to the module search path"""
import sys
from os import path
sys.path.insert(0, path.join(path.dirname(path.dirname(__file__)), 'device'))
