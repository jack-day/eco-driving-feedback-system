import pytest
import time
from pathlib import Path
from freezegun import freeze_time
from datetime import datetime, timedelta
import device  # noqa: F401
import db


# Before Each and After Each
# ------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def dbBeforeEachAndAfterEach():
    yield
    db.cur.execute('DELETE FROM driving_data')
    db.cur.execute('DELETE FROM journey')
    db.cur.execute('DELETE FROM roof_att')
    db.cur.execute('ALTER SEQUENCE journey_journey_id_seq RESTART')
    db.conn.commit()


# Mock data
# ------------------------------------------------------------------------
@pytest.fixture()
def mockRoofAtt():
    db.cur.execute("""
        INSERT INTO roof_att (name, weight, drag_coeff, frontal_area)
        VALUES (%s, %s, %s, %s) RETURNING roof_att_id
        """,
        ('test_roof_att', 10, 0.3, 0.7)
    )
    db.conn.commit()
    roofAttID = db.cur.fetchone()[0]
    return {
        'id': roofAttID,
        'name': 'test_roof_att',
        'weight': 10,
        'dragCoeff': 0.3,
        'frontalArea': 0.7
    }


@pytest.fixture()
def mockJourney():
    db.cur.execute("""
            INSERT INTO journey (passenger_cnt, cargo_weight, roof_att_id)
            VALUES (%s, %s, %s) RETURNING journey_id
        """,
        (0, 0, None)
    )
    db.conn.commit()
    journeyID = db.cur.fetchone()[0]
    return {
        'id': journeyID,
        'passengers': 0,
        'cargo': 0,
        'roofAtt': None
    }


@pytest.fixture()
def mockDrivingData(mockJourney):
    ts = datetime.now()
    db.cur.execute("""
            INSERT INTO driving_data (time, journey_id, engine_on, speed, rpm,
            fuel_level,altitude, latitude, longitude, gsi_is_indicating,
            speed_limit)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (ts, mockJourney['id'], True, 40.50, 2000, 65.75, 20.25, 43.170316,
        6.623694, False, 65)
    )
    db.conn.commit()
    return {
        'time': ts,
        'journeyID': mockJourney['id'],
        'engineOn': True,
        'speed': 40.50,
        'rpm': 2000,
        'fuelLevel': 65.75,
        'altitude': 20.25,
        'latitude': 43.170316,
        'longitude': 6.623694,
        'gsiIsIndicating': False,
        'speedLimit': 65,
        'journey': mockJourney
    }


# Helpers
# ------------------------------------------------------------------------
def updateJourneyDefaults(passengers, cargo, roofAttID=None):
    db.cur.execute("""ALTER TABLE journey
        ALTER COLUMN passenger_cnt SET DEFAULT %s""", [passengers])
    db.cur.execute("""ALTER TABLE journey
        ALTER COLUMN cargo_weight SET DEFAULT %s""", [cargo])
    db.cur.execute("""ALTER TABLE journey
        ALTER COLUMN roof_att_id SET DEFAULT %s""", [roofAttID])
    db.conn.commit()


def resetJourneyDefaults():
    updateJourneyDefaults(0, 0)


def mostRecentJourneyID():
    db.cur.execute("""SELECT currval(
        pg_get_serial_sequence('journey', 'journey_id'))""")
    db.conn.commit()
    mostRecentID = db.cur.fetchone()[0]
    return mostRecentID


def executeSQLFile(filename):
    """Execute an SQL file in the database"""
    filepath = Path(Path(__file__).resolve().parent, filename)
    with open(filepath, 'r') as file:
        db.cur.execute(file.read())
        db.conn.commit()


# Tests
# ------------------------------------------------------------------------
# getRoofAtt
# -----------------------------------
class Test_getRoofAtt:
    def test_nonExistent(self):
        roofAtt = db.getRoofAtt(0)
        assert roofAtt is None, """
            Doesn't return None when roofAtt does not exist within the database
        """

    def test_existent(self, mockRoofAtt):
        roofAtt = db.getRoofAtt(mockRoofAtt['id'])
        del mockRoofAtt['id']
        del mockRoofAtt['name']
        assert roofAtt == mockRoofAtt, """
            Doesn't return correctly when roofAtt exists within the db
        """


# journeyRowToDict
# -----------------------------------
class Test_journeyRowToDict:
    def test_baseCase(self, mockRoofAtt):
        assert db.journeyRowToDict((1, 2, 50, mockRoofAtt['id'])) == {
            'id': 1,
            'passengers': 2,
            'cargo': 50,
            'roofAtt': {
                'weight': mockRoofAtt['weight'],
                'dragCoeff': mockRoofAtt['dragCoeff'],
                'frontalArea': mockRoofAtt['frontalArea']
            }
        }

    def test_noRoofAtt(self):
        assert db.journeyRowToDict((1, 2, 50, None)) == {
            'id': 1,
            'passengers': 2,
            'cargo': 50,
            'roofAtt': None
        }, "Doesn't return correctly when given roofAtt is None"


# createJourney
# -----------------------------------
class Test_createJourney:
    def test_baseCase(self, mockRoofAtt):
        assert db.createJourney() == {
            'id': mostRecentJourneyID(),
            'passengers': 0,
            'cargo': 0,
            'roofAtt': None
        }

    def test_newDefaultValues(self, mockRoofAtt):
        updateJourneyDefaults(2, 750, mockRoofAtt['id'])

        assert db.createJourney() == {
            'id': mostRecentJourneyID(),
            'passengers': 2,
            'cargo': 750,
            'roofAtt': {
                'weight': 10,
                'dragCoeff': 0.3,
                'frontalArea': 0.7
            }
        }, "Updated default values are not used when creating new journey"

        resetJourneyDefaults()


# getJourney
# -----------------------------------
class Test_getJourney:
    def test_nonExistent(self):
        journey = db.getJourney(0)
        assert journey is None, """
            Doesn't return None when journey does not exist within the database
        """

    def test_existent(self, mockJourney):
        journey = db.getJourney(mockJourney['id'])
        assert journey == mockJourney, """
            Doesn't return correctly when journey exists within the db
        """


# getJourneyIDsWithinLastNdays
# -----------------------------------
class Test_getJourneyIDsWithinLastNdays:
    @pytest.mark.parametrize('ndays, currentTime, expectedJourneyIDs', [
        (0, '2022-02-01 00:00:00', [2]),
        (0, '2022-02-01 15:24:00', [1, 2]),
        (5, '2022-02-01 15:24:00', [1, 2, 3, 4, 5]),
        (30, '2022-02-01 15:24:00', [1, 2, 3, 4, 5, 6, 7, 8]),
        (30, '2021-12-31 23:59:59', [])
    ])
    def test_baseCase(self, ndays, currentTime, expectedJourneyIDs):
        executeSQLFile('test_data/db/getJourneyIDsWithinLastNdays.sql')
        with freeze_time(currentTime):
            assert db.getJourneyIDsWithinLastNdays(ndays) == expectedJourneyIDs


# getCurrentJourney
# -----------------------------------
class Test_getCurrentJourney:
    def test_sameJourneyID(self, mockDrivingData):
        assert db.getCurrentJourney() == mockDrivingData['journey'], """
            Doesn't return journey data from most recent driving data when it's
            timestamp is only moments ago
        """

    def test_overJourneyIntvl(self, mockDrivingData):
        # mockDrivingData needed to ensure previous driving data exists
        mockTime = datetime.now() + timedelta(seconds=db.JOURNEY_INTVL + 1)
        with freeze_time(mockTime):
            assert db.getCurrentJourney() == {
                'id': mostRecentJourneyID(),
                'passengers': 0,
                'cargo': 0,
                'roofAtt': None
            }, """
                Doesn't create a new journey when most recent driving data's
                timestamp is over the set journey interval time
            """

    def test_noDrivingData(self):
        assert db.getCurrentJourney() == {
            'id': mostRecentJourneyID(),
            'passengers': 0,
            'cargo': 0,
            'roofAtt': None
        }, "Doesn't create a new journey when no previous driving data exists"


# getJourneyApiID
# -----------------------------------
class Test_getJourneyApiID:
    def test_noApiID(self, mockJourney):
        assert db.getJourneyApiID(mockJourney['id']) is None, """
            Doesn't return None when api_journey_id is null
        """

    def test_existentApiID(self):
        db.cur.execute(
            """INSERT INTO journey (api_journey_id) VALUES (%s)
            RETURNING journey_id""",
            [5]
        )
        db.conn.commit()
        journeyID = db.cur.fetchone()[0]
        assert db.getJourneyApiID(journeyID) == 5, """
            Doesn't return existing api_journey_id correctly
        """


# updateJourneyApiID
# -----------------------------------
class Test_updateJourneyApiID:
    def test_baseCase(self, mockJourney):
        db.updateJourneyApiID(mockJourney['id'], 2)
        assert db.getJourneyApiID(mockJourney['id']) == 2, """
            api_journey_id not updated
        """

    def test_noneApiID(self, mockJourney):
        db.cur.execute(
            """INSERT INTO journey (api_journey_id) VALUES (%s)
            RETURNING journey_id""",
            [5]
        )
        db.conn.commit()
        journeyID = db.cur.fetchone()[0]
        db.updateJourneyApiID(journeyID, None)
        assert db.getJourneyApiID(mockJourney['id']) is None, """
            Doesn't set api_journey_id to null when given None
        """


# drivingDataRowToDict
# -----------------------------------
class Test_drivingDataRowToDict:
    def test_baseCase(self, mockJourney):
        time = datetime.now()
        assert db.drivingDataRowToDict((
            time, mockJourney['id'], True, 20.00, 2000, 21.00, 22.00,
            20.000001, -20.000001, True, 100
        )) == {
            'time': time,
            'journeyID': mockJourney['id'],
            'engineOn': True,
            'speed': 20.00,
            'rpm': 2000,
            'fuelLvl': 21.00,
            'alt': 22.00,
            'lat': 20.000001,
            'lng': -20.000001,
            'gsiIndicating': True,
            'spdLim': 100
        }

    def test_nullSpdLim(self, mockJourney):
        time = datetime.now()
        assert db.drivingDataRowToDict((
            time, mockJourney['id'], False, 20.00, 2000, 21.00, 22.00,
            20.000001, -20.000001, True, None
        )) == {
            'time': time,
            'journeyID': mockJourney['id'],
            'engineOn': False,
            'speed': 20.00,
            'rpm': 2000,
            'fuelLvl': 21.00,
            'alt': 22.00,
            'lat': 20.000001,
            'lng': -20.000001,
            'gsiIndicating': True,
            'spdLim': None
        }


# getJourneyDrivingData
# -----------------------------------
class Test_getJourneyDrivingData:
    @pytest.mark.parametrize('journeyID, expectedDrivingData', [
        (1, []),
        (2, [{
            'time': datetime.fromisoformat('2022-02-01 00:00:00'),
            'journeyID': 2,
            'engineOn': True,
            'speed': 10,
            'rpm': 11,
            'fuelLvl': 12,
            'alt': 13,
            'lat': 14,
            'lng': 15,
            'gsiIndicating': True,
            'spdLim': 16
        }]),
        (3, [
            {
                'time': datetime.fromisoformat('2022-02-02 00:00:00'),
                'journeyID': 3,
                'engineOn': False,
                'speed': 10,
                'rpm': 11,
                'fuelLvl': 12,
                'alt': 13,
                'lat': 14,
                'lng': 15,
                'gsiIndicating': True,
                'spdLim': 16
            },
            {
                'time': datetime.fromisoformat('2022-02-02 05:00:00'),
                'journeyID': 3,
                'engineOn': True,
                'speed': 10,
                'rpm': 11,
                'fuelLvl': 12,
                'alt': 13,
                'lat': 14,
                'lng': 15,
                'gsiIndicating': True,
                'spdLim': 16
            },
            {
                'time': datetime.fromisoformat('2022-02-02 10:00:00'),
                'journeyID': 3,
                'engineOn': True,
                'speed': 10,
                'rpm': 11,
                'fuelLvl': 12,
                'alt': 13,
                'lat': 14,
                'lng': 15,
                'gsiIndicating': True,
                'spdLim': 16
            },
            {
                'time': datetime.fromisoformat('2022-02-02 15:00:00'),
                'journeyID': 3,
                'engineOn': True,
                'speed': 10,
                'rpm': 11,
                'fuelLvl': 12,
                'alt': 13,
                'lat': 14,
                'lng': 15,
                'gsiIndicating': True,
                'spdLim': 16
            },
            {
                'time': datetime.fromisoformat('2022-02-02 20:00:00'),
                'journeyID': 3,
                'engineOn': True,
                'speed': 10,
                'rpm': 11,
                'fuelLvl': 12,
                'alt': 13,
                'lat': 14,
                'lng': 15,
                'gsiIndicating': True,
                'spdLim': 16
            },
        ]),
    ])
    def test_baseCase(self, journeyID, expectedDrivingData):
        executeSQLFile('test_data/db/getJourneyDrivingData.sql')
        assert db.getJourneyDrivingData(journeyID) == expectedDrivingData


# createDrivingData
# -----------------------------------
class Test_createDrivingData:
    def test_baseCase(self, mockJourney):
        ts = time.time()
        datetimeTs = datetime.fromtimestamp(ts)
        db.createDrivingData({
            'obdData': {
                'time': ts,
                'speed': 45.55,
                'rpm': 2000,
                'fuelLevel': 65.55,
                'alt': 22.22
            },
            'journeyID': mockJourney['id'],
            'engineOn': True,
            'coords': {
                'latitude': 50.894064,
                'longitude': -0.999009
            },
            'gsiIsIndicating': True,
            'speedLimit': 113
        })

        db.cur.execute('SELECT * FROM driving_data WHERE time=%s',
            [datetimeTs])
        assert db.cur.fetchone() == (
            datetimeTs,
            mockJourney['id'],
            True,
            45.55,
            2000,
            65.55,
            22.22,
            50.894064,
            -0.999009,
            True,
            113
        )

    def test_noSpdLim(self, mockJourney):
        ts = time.time()
        datetimeTs = datetime.fromtimestamp(ts)
        db.createDrivingData({
            'obdData': {
                'time': ts,
                'speed': 45.55,
                'rpm': 2000,
                'fuelLevel': 65.55,
                'alt': 22.22
            },
            'journeyID': mockJourney['id'],
            'engineOn': False,
            'coords': {
                'latitude': 50.894064,
                'longitude': -0.999009
            },
            'gsiIsIndicating': True,
            'speedLimit': None
        })

        db.cur.execute('SELECT * FROM driving_data WHERE time=%s',
            [datetimeTs])
        assert db.cur.fetchone() == (
            datetimeTs,
            mockJourney['id'],
            False,
            45.55,
            2000,
            65.55,
            22.22,
            50.894064,
            -0.999009,
            True,
            None
        ), "Doesn't return correctly when speed limit is None"
