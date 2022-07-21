import pytest
from unittest import mock
from pathlib import Path
from datetime import datetime
from freezegun import freeze_time
import device  # noqa: F401
import db
import performance as perf


# Mock Data
# ------------------------------------------------------------------------
@pytest.fixture(scope='module', autouse=True)
def beforeAllAndAfterAll():
    executeSQLFile('test_data/performance.sql')
    yield


def mockEmptyAccFeedback():
    """Returns a mock empty AccumlatedFeedback instance"""
    with freeze_time(dtFromISO('2020-01-01 00:00:00')):
        return perf.AccumulatedFeedback()


# Helpers
# ------------------------------------------------------------------------
def executeSQLFile(filename):
    """Execute an SQL file in the database"""
    filepath = Path(Path(__file__).resolve().parent, filename)
    with open(filepath, 'r') as file:
        db.cur.execute(file.read())
        db.conn.commit()


def secsToDatetime(secs):
    return datetime.fromtimestamp(secs)


def dtFromISO(iso):
    """Alias for datetime.fromisoformat"""
    return datetime.fromisoformat(iso)


# Mean Tests
# ------------------------------------------------------------------------
class Test_Mean:
    class Test_increment:
        @pytest.mark.parametrize('values, expectedMean', [
            ([], None),
            ([0], 0),
            ([1], 1),
            ([1, 5], 3),
            ([-1, -5], -3),
            ([-24, -16, -15, -13, -10, 9, 12, 13, 13, 15, 16, 18], 1.5),
            ([
                884941.9985416136, 486163.95481772604, -200447.9584294887,
                -632792.3471874284, -760101.7052058893, -588553.3855918685,
                -232363.8244346436, -961226.797887109, 964351.9203318947,
                -376597.243490729, 481898.4518764103, -296944.0251522388,
                -773293.6538876146, 919963.3418593293, 600101.990765844,
                -176005.13486293994, 452473.9364872349, 188316.8571159013,
                -589187.7097186446, -831151.8019055759, 679489.3969133159
            ], -36236.368525948),
            ([
                362765.34393, -507980, -910213, 533826.811383, 250728.7015028,
                531662.1266343, -939821.4385395, 864889.156, 780024.81626832,
                -320838.68, 356487.08471345, -270808.531176597,
                573152.867853475, -320920.47, -615068.1989, 254035.8994976,
                -649911.2003275, -799328.92919, 695973.57401, 388405.22666
            ], 12853.058015967)
        ])
        def test_baseCase(self, values, expectedMean):
            mean = perf.Mean()
            for value in values:
                mean.increment(value)
            assert pytest.approx(mean.value, rel=1e-6) == expectedMean

    class Test_combine:
        @pytest.mark.parametrize('mean1, mean2, expectedMean', [
            (perf.Mean(), perf.Mean(), None),
            (perf.Mean(0, 1), perf.Mean(0, 1), 0),
            (perf.Mean(1, 1), perf.Mean(), 1),
            (perf.Mean(), perf.Mean(1, 1), 1),
            (
                perf.Mean(175036.10845341, 20),
                perf.Mean(-169714.41945909, 20),
                2660.8444971619
            ),
            (
                perf.Mean(-186803.84966369, 8),
                perf.Mean(96685.533289278, 32),
                39987.656698685
            )
        ])
        def test_baseCase(self, mean1, mean2, expectedMean):
            mean1.combine(mean2)
            assert pytest.approx(mean1.value, rel=1e-6) == expectedMean


# JourneyPerformance Tests
# ------------------------------------------------------------------------
class Test_JourneyPerformance:
    # init
    # -----------------------------------
    class Test_init:
        def test_noDrivingData(self):
            journey = perf.JourneyPerformance(1)
            assert journey.journeyID == 1
            assert journey.drivingDataCount == 0
            assert journey.startTime == 0
            assert journey.endTime == 0
            assert journey.travelTime == 0
            assert journey.idleTime == 0
            assert journey.distance == 0
            assert journey.drivAccSmoothness.value is None
            assert journey.startAccSmoothness.value is None
            assert journey.decSmoothness.value is None
            assert journey.gsiAdh.value is None
            assert journey.spdLimAdh.value is None
            assert journey.motorwaySpd.value is None
            assert journey.idleDur.value is None

        def test_oneDrivingDataEntry(self):
            journey = perf.JourneyPerformance(2)
            assert journey.journeyID == 2
            assert journey.drivingDataCount == 0
            assert journey.startTime == dtFromISO('2022-02-03 00:00:00')
            assert journey.endTime == dtFromISO('2022-02-03 00:00:00')
            assert journey.travelTime == 0
            assert journey.idleTime == 0
            assert journey.distance == 0
            assert journey.drivAccSmoothness.value is None
            assert journey.startAccSmoothness.value is None
            assert journey.decSmoothness.value is None
            assert journey.gsiAdh.value is None
            assert journey.spdLimAdh.value is None
            assert journey.motorwaySpd.value is None
            assert journey.idleDur.value is None

        def test_twoDrivingDataEntries(self):
            journey = perf.JourneyPerformance(3)
            assert journey.journeyID == 3
            assert journey.drivingDataCount == 2
            assert journey.startTime == dtFromISO('2022-02-02 00:00:00')
            assert journey.endTime == dtFromISO('2022-02-02 00:00:01')
            assert journey.travelTime == 1
            assert journey.idleTime == 0
            assert pytest.approx(journey.distance, 1e-6) == 0.00277778
            assert journey.drivAccSmoothness.value is None
            assert journey.startAccSmoothness.value is None
            assert journey.decSmoothness.value is None
            assert journey.gsiAdh.value == 50
            assert journey.spdLimAdh.value == 0
            assert journey.motorwaySpd.value is None
            assert journey.idleDur.value is None

        def test_baseCase(self):
            journey = perf.JourneyPerformance(4)
            assert journey.journeyID == 4
            assert journey.drivingDataCount == 21
            assert journey.startTime == dtFromISO('2022-02-01 00:00:00')
            assert journey.endTime == dtFromISO('2022-02-01 00:00:57')
            assert journey.travelTime == 57
            assert journey.idleTime == 27
            assert pytest.approx(journey.distance, 1e-6) == 0.31263890979
            assert pytest.approx(
                journey.drivAccSmoothness.value, 1e-6) == 4.5634924285714
            assert pytest.approx(
                journey.startAccSmoothness.value, 1e-6) == 2.0833335
            assert pytest.approx(
                journey.decSmoothness.value, 1e-6) == -7.2222228
            assert pytest.approx(journey.gsiAdh.value, 1e-6) == 76.923076923
            assert pytest.approx(journey.spdLimAdh.value, 1e-6) == 83.333333333
            assert pytest.approx(journey.motorwaySpd.value, 1e-6) == 103.3
            assert journey.idleDur.value == 9

    # updAccSmoothness
    # -----------------------------------
    class Test_updAccSmoothness:
        @pytest.mark.parametrize('drivingDataPairs, expStartAccSmoothness', [
            ([({'speed': 10}, {'speed': 0})], None),
            ([({'speed': 0}, {'speed': 0.9})], None),
            ([
                (
                    {'time': secsToDatetime(0), 'speed': 0},
                    {'time': secsToDatetime(1), 'speed': 1},
                )
            ], 0.277778),
            ([
                (   # 0.277777777777778 m/s2
                    {'time': secsToDatetime(0), 'speed': 0},
                    {'time': secsToDatetime(10), 'speed': 10},
                ),
                (   # 4.16666666666667 m/s2
                    {'time': secsToDatetime(5), 'speed': 0},
                    {'time': secsToDatetime(8), 'speed': 45},
                ),
                (   # 0.185185185185185 m/s2
                    {'time': secsToDatetime(20), 'speed': 0},
                    {'time': secsToDatetime(35), 'speed': 10},
                ),
                (   # 1.77777777777778 m/s2
                    {'time': secsToDatetime(50), 'speed': 0},
                    {'time': secsToDatetime(55), 'speed': 32},
                ),
                (   # 2.92222222222222 m/s2
                    {'time': secsToDatetime(19), 'speed': 0},
                    {'time': secsToDatetime(20), 'speed': 10.52},
                )
            ], 1.8659259259259),
        ])
        def test_startAcc(self, drivingDataPairs, expStartAccSmoothness):
            journey = perf.JourneyPerformance(1)

            for pair in drivingDataPairs:
                journey.updAccSmoothness(pair[0], pair[1])

            assert (pytest.approx(journey.startAccSmoothness.value, 1e-6) ==
                expStartAccSmoothness)

        @pytest.mark.parametrize('drivingDataPairs, expDrivAccSmoothness', [
            ([({'speed': 10}, {'speed': 0})], None),
            ([({'speed': 0}, {'speed': 0.9})], None),
            ([
                (
                    {'time': secsToDatetime(0), 'speed': 5},
                    {'time': secsToDatetime(1), 'speed': 6},
                )
            ], 0.277778),
            ([
                (   # 0.277777777777778 m/s2
                    {'time': secsToDatetime(0), 'speed': 10},
                    {'time': secsToDatetime(10), 'speed': 20},
                ),
                (   # 1.52777777777778 m/s2
                    {'time': secsToDatetime(9), 'speed': 10},
                    {'time': secsToDatetime(13), 'speed': 32},
                ),
                (   # 0.148148148148148 m/s2
                    {'time': secsToDatetime(23), 'speed': 35},
                    {'time': secsToDatetime(38), 'speed': 43},
                ),
                (   # 0.833333333333332 m/s2
                    {'time': secsToDatetime(50), 'speed': 70},
                    {'time': secsToDatetime(51), 'speed': 73},
                ),
                (   # 1.81388888888889 m/s2
                    {'time': secsToDatetime(22), 'speed': 32.23},
                    {'time': secsToDatetime(23), 'speed': 38.76},
                )
            ], 0.92018518518519),
        ])
        def test_driveAcc(self, drivingDataPairs, expDrivAccSmoothness):
            journey = perf.JourneyPerformance(1)

            for pair in drivingDataPairs:
                journey.updAccSmoothness(pair[0], pair[1])

            assert (pytest.approx(journey.drivAccSmoothness.value, 1e-6) ==
                expDrivAccSmoothness)

    # updDecSmoothness
    # -----------------------------------
    class Test_updDecSmoothness:
        @pytest.mark.parametrize('drivingDataPairs, expectedDecSmoothness', [
            ([({'speed': 0}, {'speed': 10})], None),
            ([({'speed': 10}, {'speed': 9.1})], None),
            ([
                (
                    {'time': secsToDatetime(0), 'speed': 10},
                    {'time': secsToDatetime(1), 'speed': 9},
                )
            ], -0.277778),
            ([
                (   # -0.277777777777778 m/s2
                    {'time': secsToDatetime(0), 'speed': 10},
                    {'time': secsToDatetime(10), 'speed': 0},
                ),
                (   # -0.104166666666667 m/s2
                    {'time': secsToDatetime(10), 'speed': 20},
                    {'time': secsToDatetime(50), 'speed': 5},
                ),
                (   # -0.37037037037037 m/s2
                    {'time': secsToDatetime(20), 'speed': 50},
                    {'time': secsToDatetime(35), 'speed': 30},
                ),
                (   # -0.166666666666667 m/s2
                    {'time': secsToDatetime(50), 'speed': 10},
                    {'time': secsToDatetime(55), 'speed': 7},
                ),
                (   # -0.466759259259259 m/s2
                    {'time': secsToDatetime(30), 'speed': 110.52},
                    {'time': secsToDatetime(60), 'speed': 60.11},
                )
            ], -0.27714814814815),
        ])
        def test_baseCase(self, drivingDataPairs, expectedDecSmoothness):
            journey = perf.JourneyPerformance(1)

            for pair in drivingDataPairs:
                journey.updDecSmoothness(pair[0], pair[1])

            assert (pytest.approx(journey.decSmoothness.value, 1e-6) ==
                expectedDecSmoothness)

    # updGSIAdh
    # -----------------------------------
    class Test_updGSIAdh:
        @pytest.mark.parametrize('speedAndIndicatingPairs, expectedGSIAdh', [
            ([(0, None)], None),
            ([(1, True)], 0),
            ([(1, False)], 100),
            ([(10, True), (10, False)], 50),
            ([
                (10, True), (10, True), (10, True), (10, True), (10, True),
                (0, True), (0, True), (10, False), (10, False), (10, False)
            ], 37.5),
        ])
        def test_baseCase(self, speedAndIndicatingPairs, expectedGSIAdh):
            journey = perf.JourneyPerformance(1)

            for pair in speedAndIndicatingPairs:
                journey.updGSIAdh(pair[0], pair[1])

            assert journey.gsiAdh.value == expectedGSIAdh

    # updSpdLimAdh
    # -----------------------------------
    class Test_updSpdLimAdh:
        @pytest.mark.parametrize('speedAndSpdLimPairs, expectedSpdLimAdh', [
            ([(10, None)], None),
            ([(0, 100)], None),
            ([(101, 100)], 0),
            ([(100, 100)], 100),
            ([(99, 100)], 100),
            ([
                (99, 100), (30, 40), (10, None), (50, 100), (0, 70),
                (110, 100), (70, 50), (30, 20), (51, 50), (10, None),
                (50, 30), (50, 30), (50, 30), (50, 30), (50, 30), (10, None),
            ], 25),
        ])
        def test_baseCase(self, speedAndSpdLimPairs, expectedSpdLimAdh):
            journey = perf.JourneyPerformance(1)

            for pair in speedAndSpdLimPairs:
                journey.updSpdLimAdh(pair[0], pair[1])

            assert (pytest.approx(journey.spdLimAdh.value, 1e-6) ==
                expectedSpdLimAdh)

    # updMotorwaySpd
    # -----------------------------------
    class Test_updMotorwaySpd:
        @pytest.mark.parametrize('speedAndSpdLimPairs, expectedMotorwaySpd', [
            ([(10, None)], None),
            ([(30, 114)], None),
            ([(30, 113)], 30),
            ([(30, 112)], None),
            ([
                (131.32, 113), (127, 113), (58.55, 113), (67.88, 113),
                (100, 120), (86.9, 113), (80.9, 113), (24.59, 113), (113, 113),
                (50, 70), (137.33, 113), (60.63, 113), (47.42, 113), (81, 113),
                (20, 50), (142.2, 113)
            ], 89.132307692308),
        ])
        def test_baseCase(self, speedAndSpdLimPairs, expectedMotorwaySpd):
            journey = perf.JourneyPerformance(1)

            for pair in speedAndSpdLimPairs:
                journey.updMotorwaySpd(pair[0], pair[1])

            assert (pytest.approx(journey.motorwaySpd.value, 1e-6) ==
                expectedMotorwaySpd)

    # updIdle
    # -----------------------------------
    class Test_updIdle:
        @pytest.mark.parametrize('idles, expectedIdleTime, expectedIdleDur', [
            ([(secsToDatetime(0), secsToDatetime(0))], 0, None),
            ([(secsToDatetime(0), secsToDatetime(4))], 0, None),
            ([(secsToDatetime(0), secsToDatetime(5))], 5, 5),
            ([(secsToDatetime(0), secsToDatetime(6))], 6, 6),
            ([
                (secsToDatetime(0), secsToDatetime(10)),
                (secsToDatetime(0), secsToDatetime(336)),
                (secsToDatetime(20), secsToDatetime(40)),
                (secsToDatetime(30), secsToDatetime(60))
            ], 396, 99),
        ])
        def test_baseCase(self, idles, expectedIdleTime, expectedIdleDur):
            journey = perf.JourneyPerformance(1)

            for idle in idles:
                journey.updIdle(idle[0], idle[1])

            assert journey.idleTime == expectedIdleTime
            assert (pytest.approx(journey.idleDur.value, 1e-6) ==
                            expectedIdleDur)

    # updDistance
    # -----------------------------------
    class Test_updDistance:
        @pytest.mark.parametrize('drivingDataPairs, expectedDistance', [
            ([
                (
                    {'time': secsToDatetime(0), 'speed': 0},
                    {'time': secsToDatetime(0), 'speed': 0},
                )
            ], 0),
            ([
                (
                    {'time': secsToDatetime(0), 'speed': 0},
                    {'time': secsToDatetime(0), 'speed': 1},
                )
            ], 0),
            ([
                (
                    {'time': secsToDatetime(0), 'speed': 0},
                    {'time': secsToDatetime(1), 'speed': 0},
                )
            ], 0),
            ([
                (
                    {'time': secsToDatetime(0), 'speed': 10},
                    {'time': secsToDatetime(1), 'speed': 10},
                )
            ], 0.002777778),
            ([
                (
                    {'time': secsToDatetime(0), 'speed': 0},
                    {'time': secsToDatetime(1), 'speed': 10},
                )
            ], 0.001388889),
            ([
                (
                    {'time': secsToDatetime(0), 'speed': 10},
                    {'time': secsToDatetime(1), 'speed': 0},
                )
            ], 0.001388889),
            ([
                (   # 2.0833335 m
                    {'time': secsToDatetime(0), 'speed': 0},
                    {'time': secsToDatetime(1), 'speed': 15},
                ),
                (   # 37.500003 m
                    {'time': secsToDatetime(10), 'speed': 45},
                    {'time': secsToDatetime(13), 'speed': 45},
                ),
                (   # 138.8889 m
                    {'time': secsToDatetime(20), 'speed': 20},
                    {'time': secsToDatetime(40), 'speed': 30},
                ),
                (   # 38.1944475 m
                    {'time': secsToDatetime(50), 'speed': 35},
                    {'time': secsToDatetime(55), 'speed': 20},
                ),
                (   # 72.47222802 m
                    {'time': secsToDatetime(100), 'speed': 24.36},
                    {'time': secsToDatetime(110), 'speed': 27.82},
                )
            ], 0.28913891202),
        ])
        def test_baseCase(self, drivingDataPairs, expectedDistance):
            journey = perf.JourneyPerformance(1)

            for pair in drivingDataPairs:
                journey.updDistance(pair[0], pair[1])

            assert pytest.approx(journey.distance, 1e-6) == expectedDistance

    # updateAPI
    # -----------------------------------
    class Test_updateAPI:
        @pytest.fixture(autouse=True)
        def resetJourneyWithoutAPIJourneyID(self):
            db.cur.execute(
                """UPDATE journey SET api_journey_id=null
                WHERE journey_id=%s""", [7]
            )
            db.conn.commit()

        @mock.patch('api.updateJourney')
        def test_updateWithNoneValues(self, updateJourneyMock):
            journey = perf.JourneyPerformance(6)
            journey.drivingDataCount = 2
            journey.startTime = dtFromISO('2022-01-01 00:00:00')
            journey.endTime = dtFromISO('2022-01-01 01:00:00')
            journey.distance = 0.3
            journey.idleTime = 0.2
            journey.updateAPI()
            updateJourneyMock.assert_called_once_with(21, {
                'start': dtFromISO('2022-01-01 00:00:00').isoformat(),
                'end': dtFromISO('2022-01-01 01:00:00').isoformat(),
                'distance': 0.3,
                'idleSecs': 0
            })

        @mock.patch('api.updateJourney')
        def test_updateWithAllValues(self, updateJourneyMock):
            journey = perf.JourneyPerformance(6)
            journey.drivingDataCount = 2
            journey.startTime = dtFromISO('2022-01-01 00:00:00')
            journey.endTime = dtFromISO('2022-01-01 01:00:00')
            journey.distance = 8.8
            journey.idleTime = 5.7
            journey.gsiAdh.value = 0
            journey.updateAPI()
            updateJourneyMock.assert_called_once_with(21, {
                'start': dtFromISO('2022-01-01 00:00:00').isoformat(),
                'end': dtFromISO('2022-01-01 01:00:00').isoformat(),
                'distance': 8.8,
                'idleSecs': 6,
                'gsiAdh': 0,
            })

        @mock.patch('api.createJourney', return_value=46)
        def test_createWithNoneValues(self, createJourneyMock):
            journey = perf.JourneyPerformance(7)
            journey.drivingDataCount = 2
            journey.startTime = dtFromISO('2022-01-01 00:00:00')
            journey.endTime = dtFromISO('2022-01-01 01:00:00')
            journey.distance = 0.3
            journey.idleTime = 0.2
            journey.updateAPI()
            createJourneyMock.assert_called_once_with({
                'start': dtFromISO('2022-01-01 00:00:00').isoformat(),
                'end': dtFromISO('2022-01-01 01:00:00').isoformat(),
                'distance': 0.3,
                'idleSecs': 0
            })
            assert db.getJourneyApiID(7) == 46

        @mock.patch('api.createJourney', return_value=32)
        def test_createWithAllValues(self, createJourneyMock):
            journey = perf.JourneyPerformance(7)
            journey.drivingDataCount = 2
            journey.startTime = dtFromISO('2022-01-01 00:00:00')
            journey.endTime = dtFromISO('2022-01-01 01:00:00')
            journey.distance = 8.8
            journey.idleTime = 5.7
            journey.gsiAdh.value = 0
            journey.updateAPI()
            createJourneyMock.assert_called_once_with({
                'start': dtFromISO('2022-01-01 00:00:00').isoformat(),
                'end': dtFromISO('2022-01-01 01:00:00').isoformat(),
                'distance': 8.8,
                'idleSecs': 6,
                'gsiAdh': 0,
            })
            assert db.getJourneyApiID(7) == 32

        @mock.patch('api.createJourney', return_value=None)
        def test_createReturnsNone(self, createJourneyMock):
            journey = perf.JourneyPerformance(7)
            journey.drivingDataCount = 2
            journey.startTime = dtFromISO('2022-01-01 00:00:00')
            journey.endTime = dtFromISO('2022-01-01 01:00:00')
            journey.distance = 11
            journey.idleTime = 2
            journey.updateAPI()
            createJourneyMock.assert_called_once_with({
                'start': dtFromISO('2022-01-01 00:00:00').isoformat(),
                'end': dtFromISO('2022-01-01 01:00:00').isoformat(),
                'distance': 11,
                'idleSecs': 2
            })
            assert db.getJourneyApiID(7) is None

        @mock.patch('api.createJourney', return_value=32)
        def test_notCalledWhenInsufficientDrivingData(self, createJourneyMock):
            journey = perf.JourneyPerformance(7)
            journey.drivingDataCount = 1
            journey.updateAPI()
            createJourneyMock.assert_not_called()
            assert db.getJourneyApiID(7) is None


# AccumulatedFeedback Tests
# ------------------------------------------------------------------------
class Test_AccumulatedFeedback:
    # init
    # -----------------------------------
    class Test_init:
        def test_noJourneys(self):
            with freeze_time(dtFromISO('2022-01-01 00:00:00')):
                accFeedback = perf.AccumulatedFeedback()
                assert accFeedback.journeys == []
                assert accFeedback.drivingDataCount == 0
                assert accFeedback.drivAccSmoothness.value is None
                assert accFeedback.startAccSmoothness.value is None
                assert accFeedback.decSmoothness.value is None
                assert accFeedback.gsiAdh.value is None
                assert accFeedback.spdLimAdh.value is None
                assert accFeedback.motorwaySpd.value is None
                assert accFeedback.idleDur.value is None
                assert accFeedback.jrnyIdlePct.value is None
                assert accFeedback.jrnyDist.value is None

        def test_baseCase(self):
            with freeze_time(dtFromISO('2022-02-01 12:00:00')):
                accFeedback = perf.AccumulatedFeedback()
                assert len(accFeedback.journeys) == 2
                assert accFeedback.drivingDataCount == 29
                assert pytest.approx(
                    accFeedback.drivAccSmoothness.value, 1e-6) == 5.20833375
                assert pytest.approx(
                    accFeedback.startAccSmoothness.value, 1e-6) == 2.777778
                assert pytest.approx(
                    accFeedback.decSmoothness.value, 1e-6) == -6.27314865
                assert pytest.approx(
                    accFeedback.gsiAdh.value, 1e-6) == 72.222222222
                assert accFeedback.spdLimAdh.value == 81.25
                assert pytest.approx(
                    accFeedback.motorwaySpd.value, 1e-6) == 105.21428571429
                assert accFeedback.idleDur.value == 28
                assert pytest.approx(
                    accFeedback.jrnyIdlePct.value, 1e-6) == 59.10087719
                assert pytest.approx(
                    accFeedback.jrnyDist.value, 1e-6) == 0.486180592395

        @mock.patch('db.updateJourneyApiID')
        @mock.patch('api.createJourney', return_value=32)
        def test_currentJrnyAPIUpd(self, createJourneyMock, updateApiIDMock):
            with freeze_time(dtFromISO('2022-03-04 12:00:00')):
                accFeedback = perf.AccumulatedFeedback({'id': 3})
                assert len(accFeedback.journeys) == 2
                createJourneyMock.assert_called_once_with({
                    'start': dtFromISO('2022-02-02 00:00:00').isoformat(),
                    'end': dtFromISO('2022-02-02 00:00:01').isoformat(),
                    'distance': pytest.approx(0.00277778, 1e-6),
                    'idleSecs': 0,
                    'gsiAdh': 50
                })
                updateApiIDMock.assert_called_once_with(3, 32)

    # addJourney
    # -----------------------------------
    class Test_addJourney:
        def test_noDrivingData(self):
            journey = perf.JourneyPerformance(1)
            accFeedback = perf.AccumulatedFeedback()
            accFeedback.addJourney(journey)
            assert accFeedback.journeys == [journey]
            assert accFeedback.drivingDataCount == 0
            assert accFeedback.drivAccSmoothness.value is None
            assert accFeedback.startAccSmoothness.value is None
            assert accFeedback.decSmoothness.value is None
            assert accFeedback.gsiAdh.value is None
            assert accFeedback.spdLimAdh.value is None
            assert accFeedback.motorwaySpd.value is None
            assert accFeedback.idleDur.value is None
            assert accFeedback.jrnyIdlePct.value is None
            assert accFeedback.jrnyDist.value is None

        def test_oneDrivingDataEntry(self):
            journey = perf.JourneyPerformance(2)
            accFeedback = perf.AccumulatedFeedback()
            accFeedback.addJourney(journey)
            assert accFeedback.journeys == [journey]
            assert accFeedback.drivingDataCount == 0
            assert accFeedback.drivAccSmoothness.value is None
            assert accFeedback.startAccSmoothness.value is None
            assert accFeedback.decSmoothness.value is None
            assert accFeedback.gsiAdh.value is None
            assert accFeedback.spdLimAdh.value is None
            assert accFeedback.motorwaySpd.value is None
            assert accFeedback.idleDur.value is None
            assert accFeedback.jrnyIdlePct.value is None
            assert accFeedback.jrnyDist.value is None

        def test_twoDrivingDataEntries(self):
            journey = perf.JourneyPerformance(3)
            accFeedback = perf.AccumulatedFeedback()
            accFeedback.addJourney(journey)
            assert accFeedback.journeys == [journey]
            assert accFeedback.drivingDataCount == 2
            assert accFeedback.drivAccSmoothness.value is None
            assert accFeedback.startAccSmoothness.value is None
            assert accFeedback.decSmoothness.value is None
            assert accFeedback.gsiAdh.value == 50
            assert accFeedback.spdLimAdh.value == 0
            assert accFeedback.motorwaySpd.value is None
            assert accFeedback.idleDur.value is None
            assert accFeedback.jrnyIdlePct.value == 0
            assert pytest.approx(
                accFeedback.jrnyDist.value, 1e-6) == 0.00277778

        def test_existingValues(self):
            accFeedback = perf.AccumulatedFeedback()
            accFeedback.drivingDataCount = 3
            accFeedback.drivAccSmoothness.increment(1)
            accFeedback.startAccSmoothness.increment(2)
            accFeedback.decSmoothness.increment(-1)
            accFeedback.gsiAdh.increment(100)
            accFeedback.spdLimAdh.increment(100)
            accFeedback.motorwaySpd.increment(80)
            accFeedback.idleDur.increment(10)
            accFeedback.jrnyIdlePct.increment(5)
            accFeedback.jrnyDist.increment(1)

            journey = perf.JourneyPerformance(3)
            accFeedback.addJourney(journey)
            assert accFeedback.journeys == [journey]
            assert accFeedback.drivingDataCount == 5
            assert accFeedback.drivAccSmoothness.value == 1
            assert accFeedback.startAccSmoothness.value == 2
            assert accFeedback.decSmoothness.value == -1
            assert pytest.approx(
                accFeedback.gsiAdh.value, 1e-6) == 66.6666666667
            assert accFeedback.spdLimAdh.value == 50
            assert accFeedback.motorwaySpd.value == 80
            assert accFeedback.idleDur.value == 10
            assert accFeedback.jrnyIdlePct.value == 2.5
            assert pytest.approx(
                accFeedback.jrnyDist.value, 1e-6) == 0.50138889

    # calcLinearScore
    # -----------------------------------
    class Test_calcLinearScore:
        @pytest.mark.parametrize('value, min, max, reverseScore, expScore', [
            (-1, 0, 100, False, 0),
            (0, 0, 100, False, 0),
            (1, 0, 100, False, 1),
            (50, 0, 100, False, 50),
            (99, 0, 100, False, 99),
            (100, 0, 100, False, 100),
            (101, 0, 100, False, 100),
            (25, 0, 100, True, 75),
        ])
        def test_baseCase(self, value, min, max, reverseScore, expScore):
            assert perf.AccumulatedFeedback.calcLinearScore(
                value, min, max, reverseScore) == expScore

        def test_noneValue(self):
            assert perf.AccumulatedFeedback.calcLinearScore(None, 0, 0) is None

    # Factor Scores
    # -----------------------------------
    class Test_FactorScores:
        @pytest.mark.parametrize('drivAccSmthness, expectedScore', [
            (None, None),
            (1.4706, 0),
            (1.4705, 0),
            (1.457795, 1),
            (0.83525, 50),
            (0.212705, 99),
            (0.2, 100),
            (0.187295, 100)
        ])
        def test_drivAccSmoothnessScore(self, drivAccSmthness, expectedScore):
            accFeedback = mockEmptyAccFeedback()
            accFeedback.drivAccSmoothness.value = drivAccSmthness
            accFeedback.updFactorScores()
            assert accFeedback.drivAccSmoothnessScore == expectedScore

        @pytest.mark.parametrize('startAccSmthness, expScore', [
            (None, None),
            (2.62198, 0),
            (2.598, 0),
            (2.57402, 1),
            (1.399, 50),
            (0.22398, 99),
            (0.2, 100),
            (0.17602, 100)
        ])
        def test_startAccSmoothnessScore(self, startAccSmthness, expScore):
            accFeedback = mockEmptyAccFeedback()
            accFeedback.startAccSmoothness.value = startAccSmthness
            accFeedback.updFactorScores()
            assert accFeedback.startAccSmoothnessScore == expScore

        @pytest.mark.parametrize('decSmoothness, expectedScore', [
            (None, None),
            (-6.7852, 0),
            (-6.72, 0),
            (-6.6548, 1),
            (-3.46, 50),
            (-0.2652, 99),
            (-0.2, 100),
            (-0.1348, 100)
        ])
        def test_decSmoothnessScore(self, decSmoothness, expectedScore):
            accFeedback = mockEmptyAccFeedback()
            accFeedback.decSmoothness.value = decSmoothness
            accFeedback.updFactorScores()
            assert accFeedback.decSmoothnessScore == expectedScore

        @pytest.mark.parametrize('gsiAdh, expectedScore', [
            (None, None),
            (-1, 0),
            (0, 0),
            (1, 1),
            (50, 50),
            (99, 99),
            (100, 100),
            (101, 100)
        ])
        def test_gsiAdhScore(self, gsiAdh, expectedScore):
            accFeedback = mockEmptyAccFeedback()
            accFeedback.gsiAdh.value = gsiAdh
            accFeedback.updFactorScores()
            assert accFeedback.gsiAdhScore == expectedScore

        @pytest.mark.parametrize('spdLimAdh, expectedScore', [
            (None, None),
            (-1, 0),
            (0, 0),
            (1, 1),
            (50, 50),
            (99, 99),
            (100, 100),
            (101, 100)
        ])
        def test_spdLimAdhScore(self, spdLimAdh, expectedScore):
            accFeedback = mockEmptyAccFeedback()
            accFeedback.spdLimAdh.value = spdLimAdh
            accFeedback.updFactorScores()
            assert accFeedback.spdLimAdhScore == expectedScore

        @pytest.mark.parametrize('motorwaySpdMph, expectedScore', [
            (None, None),
            (76.0666667, 0),
            (75, 0),
            (74.9333333, 1),
            (72.5, 38),
            (70.0666667, 74),
            (70, 75),
            (69.6, 76),
            (65, 88),
            (60.4, 99),
            (60, 100),
            (59.6, 100)
        ])
        def test_motorwaySpdScore(self, motorwaySpdMph, expectedScore):
            accFeedback = mockEmptyAccFeedback()
            if motorwaySpdMph is not None:
                accFeedback.motorwaySpd.value = motorwaySpdMph * 1.60934  # kmh
            accFeedback.updFactorScores()
            assert pytest.approx(
                accFeedback.motorwaySpdScore, 1e-6) == expectedScore

        @pytest.mark.parametrize('idleDur, expectedScore', [
            (None, None),
            (60.55, 0),
            (60, 0),
            (59.55, 1),
            (32.5, 50),
            (5.55, 99),
            (5, 100),
            (4.55, 100)
        ])
        def test_idleDurScore(self, idleDur, expectedScore):
            accFeedback = mockEmptyAccFeedback()
            accFeedback.idleDur.value = idleDur
            accFeedback.updFactorScores()
            assert accFeedback.idleDurScore == expectedScore

        @pytest.mark.parametrize('jrnyIdlePct, expectedScore', [
            (None, None),
            (101, 0),
            (100, 0),
            (99, 1),
            (50, 50),
            (1, 99),
            (0, 100),
            (-1, 100)
        ])
        def test_jrnyIdlePctScore(self, jrnyIdlePct, expectedScore):
            accFeedback = mockEmptyAccFeedback()
            accFeedback.jrnyIdlePct.value = jrnyIdlePct
            accFeedback.updFactorScores()
            assert accFeedback.jrnyIdlePctScore == expectedScore

        @pytest.mark.parametrize('jrnyDist, expectedScore', [
            (None, None),
            (1.97, 0),
            (2, 0),
            (2.03, 1),
            (3.5, 50),
            (4.97, 99),
            (5, 100),
            (5.03, 100)
        ])
        def test_jrnyDistScore(self, jrnyDist, expectedScore):
            accFeedback = mockEmptyAccFeedback()
            accFeedback.jrnyDist.value = jrnyDist
            accFeedback.updFactorScores()
            assert accFeedback.jrnyDistScore == expectedScore

    # Overall eco-driving score
    # -----------------------------------
    class Test_ecoDrivingScore:
        def test_noScores(self):
            accFeedback = mockEmptyAccFeedback()
            accFeedback.updEcoDrivingScore()
            assert accFeedback.ecoDrivingScore == 100

        def test_someNone(self):
            accFeedback = mockEmptyAccFeedback()
            accFeedback.drivAccSmoothnessScore = 67
            accFeedback.startAccSmoothnessScore = 23
            accFeedback.gsiAdhScore = 44
            accFeedback.jrnyIdlePctScore = 100
            accFeedback.jrnyDistScore = 12
            accFeedback.updEcoDrivingScore()
            assert accFeedback.ecoDrivingScore == 58

        def test_allScores(self):
            accFeedback = mockEmptyAccFeedback()
            accFeedback.drivAccSmoothnessScore = 80
            accFeedback.startAccSmoothnessScore = 60
            accFeedback.decSmoothnessScore = 72
            accFeedback.gsiAdhScore = 45
            accFeedback.spdLimAdhScore = 100
            accFeedback.motorwaySpdScore = 81
            accFeedback.idleDurScore = 0
            accFeedback.jrnyIdlePctScore = 3
            accFeedback.jrnyDistScore = 66
            accFeedback.updEcoDrivingScore()
            assert accFeedback.ecoDrivingScore == 62

    # updateAPI
    # -----------------------------------
    class Test_updateAPI:
        @mock.patch('api.addScores')
        def test_noFactorScores(self, addScoresMock):
            calculatedAt = dtFromISO('2022-01-01 00:00:00+00:00')
            with freeze_time(calculatedAt):
                accFeedback = perf.AccumulatedFeedback()
                accFeedback.drivingDataCount = 2
                accFeedback.ecoDrivingScore = 78
                accFeedback.updateAPI()
                assert addScoresMock.called_once_with({
                    'calculatedAt': calculatedAt.isoformat(),
                    'ecoDriving': 78
                })

        @mock.patch('api.addScores')
        def test_someNone(self, addScoresMock):
            calculatedAt = dtFromISO('2022-01-01 00:00:00+00:00')
            with freeze_time(calculatedAt):
                accFeedback = perf.AccumulatedFeedback()
                accFeedback.drivingDataCount = 2
                accFeedback.ecoDrivingScore = 1
                accFeedback.drivAccSmoothnessScore = 12
                accFeedback.startAccSmoothnessScore = 25
                accFeedback.gsiAdhScore = 33
                accFeedback.jrnyIdlePctScore = 80
                accFeedback.jrnyDistScore = 66
                accFeedback.updateAPI()
                assert addScoresMock.called_once_with({
                    'calculatedAt': calculatedAt.isoformat(),
                    'ecoDriving': 1,
                    'drivAccSmoothness': 12,
                    'startAccSmoothness': 25,
                    'gsiAdh': 33,
                    'journeyIdlePct': 80,
                    'journeyDistance': 66
                })

        @mock.patch('api.addScores')
        def test_allScores(self, addScoresMock):
            calculatedAt = dtFromISO('2022-01-01 00:00:00+00:00')
            with freeze_time(calculatedAt):
                accFeedback = perf.AccumulatedFeedback()
                accFeedback.drivingDataCount = 2
                accFeedback.ecoDrivingScore = 76
                accFeedback.drivAccSmoothnessScore = 32
                accFeedback.startAccSmoothnessScore = 45
                accFeedback.decSmoothnessScore = 40
                accFeedback.gsiAdhScore = 81
                accFeedback.spdLimAdhScore = 56
                accFeedback.motorwaySpdScore = 71
                accFeedback.idleDurScore = 0
                accFeedback.jrnyIdlePctScore = 100
                accFeedback.jrnyDistScore = 9
                accFeedback.updateAPI()
                assert addScoresMock.called_once_with({
                    'calculatedAt': calculatedAt.isoformat(),
                    'ecoDriving': 76,
                    'drivAccSmoothness': 32,
                    'startAccSmoothness': 45,
                    'decSmoothness': 40,
                    'gsiAdh': 81,
                    'speedLimitAdh': 56,
                    'motorwaySpeed': 71,
                    'idleDuration': 0,
                    'journeyIdlePct': 100,
                    'journeyDistance': 9
                })

        @mock.patch('api.addScores')
        def test_notCalledWhenInsufficientDrivingData(self, addScoresMock):
            accFeedback = perf.AccumulatedFeedback()
            accFeedback.drivingDataCount = 1
            accFeedback.updateAPI()
            addScoresMock.assert_not_called()
