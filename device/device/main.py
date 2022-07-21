"""
Device Main Application

References
----------
.. [1] Portland State Aerospace Society. (2004). A Quick Derivation relating
   altitude to air pressure. Version 1.03.
   http://psas.pdx.edu/RocketScience/PressureAltitude_Derived.pdf.
"""
import time
import requests
import db
from obd_ii import OBDConnect, obd
from gsi import GSI
from gps import getGPSCoords
from performance import AccumulatedFeedback
from display import Display
from config import CONFIG
from settings import SETTINGS

DRIVING_DATA_INTVL = 1  # Second
SPD_LIM_FETCH_INTVL = 3  # Seconds
ACC_FEEDBACK_INTVL = 60  # Seconds


# Retrieving Data
# -------------------------------------------------------------------------
def getOBDData(obdConn):
    """Retrieves required OBD data"""
    pressure = obdConn.query(obd.commands.BAROMETRIC_PRESSURE).value
    return {
        'rpm': obdConn.query(obd.commands.RPM).value,
        'speed': obdConn.query(obd.commands.SPEED).value,  # kph
        'throttle': obdConn.query(obd.commands.THROTTLE_POS).value,  # percent
        'fuelLevel': obdConn.query(obd.commands.FUEL_LEVEL).value,  # percent
        'alt': 44330.8 - (4946.54 * (pressure ** 0.1902632)),  # metres [1]
    }


def getMostConfidentRoute(matchings):
    """Retrieves the route with the highest confidence for matchings received
    from Mapbox"""
    highestConfidence = 0
    route = None

    for match in matchings:
        if match['confidence'] > highestConfidence:
            highestConfidence = match['confidence']
            route = match

    return route


def getSpeedLimit(coords, prevCoords):
    """Retrieves the speed limit for the route of the given coordinates using
    Mapbox's map matching API"""
    currCoordsStr = f'{coords["longitude"]},{coords["latitude"]}'
    prevCoordsStr = f'{prevCoords["longitude"]},{prevCoords["latitude"]}'
    coordsStr = f'{currCoordsStr};{prevCoordsStr}'

    try:
        response = requests.get(
            f'https://api.mapbox.com/matching/v5/mapbox/driving/{coordsStr}', {
                'annotations': 'maxspeed',
                'overview': 'full',
                'access_token': CONFIG['mapboxAccessToken']
            },
            timeout=5
        )

        if response.ok:
            data = response.json()
            if data['code'] == "Ok":
                route = getMostConfidentRoute(data['matchings'])
                maxSpd = route['legs'][0]['annotation']['maxspeed']
                speedLimit = maxSpd[0]

                if speedLimit['unit'] == 'km/h':
                    return speedLimit['speed']
                elif speedLimit['unit'] == 'mph':
                    return speedLimit['speed'] * 1.609344
    except Exception:
        pass


# Main Loop
# -------------------------------------------------------------------------
if __name__ == '__main__':
    obdConn = OBDConnect()
    journey = db.getCurrentJourney()
    gsi = GSI(SETTINGS, journey)
    display = Display(gsi, AccumulatedFeedback(journey))
    prevOBDData = None
    prevCoords = None
    prevSpdLim = None
    prevSpdLimFetchTs = time.time() - SPD_LIM_FETCH_INTVL
    prevDrivingDataEntryTs = time.time() - DRIVING_DATA_INTVL
    prevAccFeedbackUpd = time.time()

    try:
        while obdConn.is_connected:
            ts = time.time()
            obdData = getOBDData(obdConn)
            obdData['time'] = ts
            coords = getGPSCoords()

            if prevOBDData:
                gsi.update(obdData, prevOBDData)

            if prevCoords and ts - prevSpdLimFetchTs >= SPD_LIM_FETCH_INTVL:
                speedLimit = getSpeedLimit(coords, prevCoords)
                prevSpdLim = speedLimit
                prevSpdLimFetchTs = ts
            else:
                speedLimit = prevSpdLim

            if ts - prevDrivingDataEntryTs >= DRIVING_DATA_INTVL:
                db.createDrivingData({
                    'obdData': obdData,
                    'journeyID': journey['id'],
                    'engineOn': True,
                    'coords': coords,
                    'gsiIsIndicating': gsi.isIndicating,
                    'speedLimit': speedLimit
                })
                prevDrivingDataEntryTs = ts

            if ts - prevAccFeedbackUpd >= ACC_FEEDBACK_INTVL:
                display.accumulatedFeedback = AccumulatedFeedback(journey)
                prevAccFeedbackUpd = ts

            prevOBDData = obdData
            prevCoords = coords
    except BrokenPipeError:
        print('OBD-II Disconnected')
    finally:
        print('Exiting...')
        display.stop()
        db.createDrivingData({
            'obdData': prevOBDData,
            'journeyID': journey['id'],
            'engineOn': False,
            'coords': prevCoords,
            'gsiIsIndicating': None,
            'speedLimit': prevSpdLim
        })
        AccumulatedFeedback(journey)  # Send latest data to API
        db.conn.close()
