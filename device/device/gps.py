"""
GPS Coordinate Simulation

Simulates GPS data from gps.yaml in place of a GPS library
due to no currently implemented GPS hardware.
"""
from pathlib import Path
import time
import yaml
from config import CONFIG

# Retreive set gps data
gpsFile = Path(Path(__file__).resolve().parent.parent, CONFIG['gpsFile'])
with open(gpsFile, 'r') as file:
    gps = yaml.safe_load(file)

startTime = time.time()
timeIntvls = sorted([x for x in gps.keys()])


def getGPSCoords():
    """
    Retreives simulated GPS coordinates based on the time since script start

    The GPS coordinates have time intervals that are used as keys. We select
    the GPS coordinates to be returned by comparing the time intervals to the
    time since the program started running. This time difference is modulo the
    highest set time interval so that the GPS coordinates are infinitely
    looped. If the time difference is inbetween the set time intervals, the GPS
    coordinates are interpolated.
    """
    currTime = time.time()

    # Round to nearest millisecond to avoid smaller fractions
    # causing minuscule errors in interpolation
    timeSinceStart = round(currTime - startTime, 3) % timeIntvls[-1]

    # Loop though each time interval
    for i in range(len(timeIntvls)):
        timeIntvl = timeIntvls[i]
        coords = gps[timeIntvl]
        nextTimeIntvl = timeIntvls[i + 1]
        nextCoords = gps[nextTimeIntvl]

        if timeIntvl <= timeSinceStart and timeSinceStart < nextTimeIntvl:
            timeIntvlDiff = timeSinceStart - timeIntvl
            pctDiff = timeIntvlDiff / (nextTimeIntvl - timeIntvl)
            latDiff = nextCoords['latitude'] - coords['latitude']
            lngDiff = nextCoords['longitude'] - coords['longitude']
            return {
                'latitude': coords['latitude'] + (latDiff * pctDiff),
                'longitude': coords['longitude'] + (lngDiff * pctDiff)
            }
