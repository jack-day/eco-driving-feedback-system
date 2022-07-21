"""
Utility functions

Provides simple helper/utility functions that are used throughout the programs
modules and do not alter its state.
"""


def kmhToMps(kmh):
    """Converts kilometers/hour to metres/second"""
    return kmh * (5 / 18)
