"""
Database Interaction

Provides a connection to the database and functions to retrieve and alter
data stored in it.
"""
import psycopg2
import time
from datetime import datetime, timedelta
from config import CONFIG

conn = psycopg2.connect(
    host=CONFIG['dbHost'],
    database=CONFIG['dbDatabase'],
    user=CONFIG['dbUser'],
    password=CONFIG['dbPassword']
)

cur = conn.cursor()


# Roof Attachments
# -------------------------------------------------------------------------
def getRoofAtt(id):
    """Retrieves a roof attachment with a given id from the database"""
    cur.execute("""SELECT weight, drag_coeff, frontal_area FROM roof_att
        WHERE roof_att_id=%s""", [id])
    conn.commit()

    roofAtt = cur.fetchone()
    if roofAtt:
        return {
            'weight': roofAtt[0],
            'dragCoeff': roofAtt[1],
            'frontalArea': roofAtt[2]
        }


# Journey
# -------------------------------------------------------------------------
JOURNEY_INTVL = 10 * 60  # Seconds
"""Time interval between driving data entries at which a new journey should be
created"""


def journeyRowToDict(row):
    """Coverts a row from the journey table into a dictionary with standardised
    keys"""
    if row[3]:
        roofAtt = getRoofAtt(row[3])
    else:
        roofAtt = None

    return {
        'id': row[0],
        'passengers': row[1],
        'cargo': row[2],
        'roofAtt': roofAtt
    }


def createJourney():
    """Creates a new journey entry in the database, returning it's data"""
    cur.execute("""INSERT INTO journey DEFAULT VALUES
        RETURNING journey_id, passenger_cnt, cargo_weight, roof_att_id""")
    conn.commit()
    journey = cur.fetchone()
    return journeyRowToDict(journey)


def getJourney(id):
    """Retrieves a journey with a given id from the database"""
    cur.execute("""SELECT journey_id, passenger_cnt, cargo_weight, roof_att_id
        FROM journey WHERE journey_id=%s""", [id])
    conn.commit()

    journey = cur.fetchone()
    if journey:
        return journeyRowToDict(journey)


def getJourneyIDsWithinLastNdays(ndays):
    """Retrieves the IDs of all journeys that started in the last n days"""
    now = datetime.now()
    ndaysAgo = now - timedelta(days=ndays)

    # ndaysAgo at 00:00
    ndaysAgoMidnight = datetime.combine(ndaysAgo, datetime.min.time())

    cur.execute("""SELECT journey_id FROM journey_start_times
        WHERE start_time BETWEEN %s AND %s""", [ndaysAgoMidnight, now])
    conn.commit()

    return [journey[0] for journey in cur.fetchall()]


def getCurrentJourney():
    """Retrieves the current journey based on the timestamp of the most recent
    driving data entry"""
    cur.execute("""SELECT time, journey_id FROM driving_data
        ORDER BY time DESC LIMIT 1""")
    conn.commit()
    mostRecentDrivingData = cur.fetchone()

    if (
        mostRecentDrivingData is None or
        time.time() - mostRecentDrivingData[0].timestamp() >= JOURNEY_INTVL
    ):
        return createJourney()
    else:
        return getJourney(mostRecentDrivingData[1])


def getJourneyApiID(journeyID):
    """Retrieves the API journey ID from a journey with a given id"""
    cur.execute(
        'SELECT api_journey_id FROM journey WHERE journey_id=%s',
        [journeyID]
    )
    conn.commit()
    journey = cur.fetchone()
    return journey[0]


def updateJourneyApiID(journeyID, apiJourneyID):
    """Updates the API journey ID of a journey with a given id"""
    cur.execute(
        'UPDATE journey SET api_journey_id=%s WHERE journey_id=%s',
        [apiJourneyID, journeyID]
    )
    conn.commit()


# Driving Data
# -------------------------------------------------------------------------
def drivingDataRowToDict(row):
    """Coverts a row from the driving data table into a dictionary with
    standardised keys"""
    return {
        'time': row[0],
        'journeyID': row[1],
        'engineOn': row[2],
        'speed': row[3],
        'rpm': row[4],
        'fuelLvl': row[5],
        'alt': row[6],
        'lat': row[7],
        'lng': row[8],
        'gsiIndicating': row[9],
        'spdLim': row[10]
    }


def getJourneyDrivingData(journeyID):
    """Retrieves all driving data from a given journey"""
    cur.execute("""SELECT
            time,
            journey_id,
            engine_on,
            speed,
            rpm,
            fuel_level,
            altitude,
            latitude,
            longitude,
            gsi_is_indicating,
            speed_limit
        FROM driving_data WHERE journey_id=%s""",
        [journeyID]
    )
    conn.commit()
    return [drivingDataRowToDict(row) for row in cur.fetchall()]


def createDrivingData(data):
    """Creates a new driving data entry in the database"""
    cur.execute("""
        INSERT INTO driving_data (time, journey_id, engine_on, speed, rpm,
            fuel_level, altitude, latitude, longitude, gsi_is_indicating,
            speed_limit)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            datetime.fromtimestamp(data['obdData']['time']),
            data['journeyID'],
            data['engineOn'],
            data['obdData']['speed'],
            data['obdData']['rpm'],
            data['obdData']['fuelLevel'],
            data['obdData']['alt'],
            data['coords']['latitude'],
            data['coords']['longitude'],
            data['gsiIsIndicating'],
            data['speedLimit']
        )
    )
    conn.commit()
