import pytest
import device  # noqa: F401
from gsi import GSI
from settings import SETTINGS


# Mock data
# ------------------------------------------------------------------------
@pytest.fixture
def gsi():
    return GSI(SETTINGS, {
        'passengers': 2,
        'cargo': 750,
        'roofAtt': {
            'weight': 250,
            'dragCoeff': 0.2,
            'frontalArea': 0.5
        }
    })


@pytest.fixture
def gsiNoRoofAtt():
    return GSI(SETTINGS, {
        'passengers': 2,
        'cargo': 750,
        'roofAtt': None
    })


# Tests
# ------------------------------------------------------------------------
class Test_GSI:
    # isIndicating
    # -----------------------------------
    class Test_isIndicating:
        def test_noThrottle(self, gsi):
            assert gsi.isIndicating is None

        def test_isNotIndicating(self, gsi):
            gsi.throttleActive = True
            assert gsi.isIndicating is False

        def test_isIndicating(self, gsi):
            gsi.throttleActive = True
            gsi.dotDispCnt = gsi.half
            assert gsi.isIndicating is True

    # getCurrentGear
    # -----------------------------------
    @pytest.mark.parametrize('rpm, kmh, expectedGear', [
        (2000, 0, 1),
        (2020, 20, 0),  # 101 gear ratio
        (2000, 20, 0),  # 100 gear ratio (Reverse)
        (1520, 20, 0),  # 76 gear ratio
        (1500, 20, 0),  # 75 gear ratio
        (1480, 20, 1),  # 74 gear ratio
        (2000, 40, 1),  # 50 gear ratio (1st)
        (1640, 40, 1),  # 41 gear ratio
        (1600, 40, 1),  # 40 gear ratio
        (1560, 40, 2),  # 39 gear ratio
        (1200, 40, 2),  # 30 gear ratio (2nd)
        (1560, 60, 2),  # 26 gear ratio
        (1500, 60, 2),  # 25 gear ratio
        (1440, 60, 3),  # 24 gear ratio
        (2000, 100, 3)  # 20 gear ratio (3rd)
    ])
    def test_getCurrentGear(self, rpm, kmh, expectedGear, gsi):
        assert gsi.getCurrentGear(rpm, kmh) == expectedGear

    # getVehicleMass
    # -----------------------------------
    class Test_getVehicleMass:
        def test_baseCase(self, gsi):
            assert gsi.getVehicleMass() == (500 + 750 + (3 * 75) + 250)

        def test_noRoofAtt(self, gsiNoRoofAtt):
            assert gsiNoRoofAtt.getVehicleMass() == 500 + 750 + (3 * 75)

    # calcDrag
    # -----------------------------------
    @pytest.mark.parametrize('frontalArea, dragCoeff, speed, expectedDrag', [
        (0, 0, 0, 0),
        (0, 1, 1, 0),
        (1, 0, 0, 0),
        (1, 1, 0, 0),
        (2, 0.35, 14, 82.457),
        (4, 0.5, 20, 480.8),
        (1, 0.3, 1, 0.180)
    ])
    def test_calcDrag(self, frontalArea, dragCoeff, speed, expectedDrag, gsi):
        drag = gsi.calcDrag(frontalArea, dragCoeff, speed)
        assert round(drag, 3) == expectedDrag

    # calcTracEff
    # -----------------------------------
    class Test_calcTracEff:
        @pytest.mark.parametrize(
            'obdData, prevOBDData, grade, expectedTracEff', [
                (
                    {'time': 0, 'speed': 0}, {'time': 0, 'speed': 0}, 0,
                    169.22
                ),
                (
                    {'time': 10, 'speed': 10}, {'time': 0, 'speed': 0}, 0,
                    690.43
                ),
                (
                    {'time': 10, 'speed': 10}, {'time': 0, 'speed': 0}, .5,
                    8782.68
                ),
                (
                    {'time': 30, 'speed': 5}, {'time': 10, 'speed': 10}, .3,
                    5163.46
                ),
                (
                    {'time': 10, 'speed': 10}, {'time': 0, 'speed': 0}, -.3,
                    -4317.99
                )
            ]
        )
        def test_baseCase(self, obdData, prevOBDData, grade, expectedTracEff,
                            gsi):
            tracEff = gsi.calcTracEff(obdData, prevOBDData, grade)
            assert round(tracEff, 2) == expectedTracEff

        def test_noRoofAtt(self, gsiNoRoofAtt):
            assert round(gsiNoRoofAtt.calcTracEff(
                {'time': 10, 'speed': 10},
                {'time': 0, 'speed': 0},
                0
            ), 2) == 590.44

    # calcUpshiftRPM
    # -----------------------------------
    class Test_calcUpshiftRPM:
        @pytest.mark.parametrize('obdData, prevOBDData, expectedRPM', [
            (
                {'time': 10, 'rpm': 2500, 'speed': 50, 'throttle': 80,
                'alt': 10},
                {'time': 0, 'rpm': 1500, 'speed': 30, 'throttle': 40,
                'alt': 10},
                2000
            ),
            (
                {'time': 30, 'rpm': 2000, 'speed': 40, 'throttle': 40,
                'alt': 5},
                {'time': 15, 'rpm': 1500, 'speed': 30, 'throttle': 10,
                'alt': 10},
                2000
            ),
            (
                {'time': 15, 'rpm': 2500, 'speed': 50, 'throttle': 100,
                'alt': 20},
                {'time': 5, 'rpm': 2000, 'speed': 40, 'throttle': 70,
                'alt': 10},
                2692.23
            ),
            (
                {'time': 30, 'rpm': 1500, 'speed': 30, 'throttle': 10,
                'alt': 20},
                {'time': 10, 'rpm': 1750, 'speed': 35, 'throttle': 70,
                'alt': 10},
                3846.96
            ),
            (
                {'time': 15, 'rpm': 2500, 'speed': 50, 'throttle': 100,
                'alt': 40},
                {'time': 5, 'rpm': 2000, 'speed': 40, 'throttle': 70,
                'alt': 10},
                4000
            ),
        ])
        def test_baseCase(self, obdData, prevOBDData, expectedRPM, gsi):
            upshiftRPM = gsi.calcUpshiftRPM(obdData, prevOBDData)
            assert round(upshiftRPM, 2) == expectedRPM

    # update
    # -----------------------------------
    class Test_update:
        @pytest.mark.parametrize('obdData, prevOBDData, assertMsg', [
            (
                {'rpm': 2000, 'speed': 20, 'throttle': 100}, {},
                "Indicated when in reverse gear"
            ),
            (
                {'rpm': 2000, 'speed': 100, 'throttle': 100}, {},
                "Indicated when in highest gear"
            ),
            (
                {'rpm': 2000, 'speed': 0, 'throttle': 100}, {},
                "Indicated when speed was less than 1 kph"
            )
        ])
        def test_doesNotIndicate(self, obdData, prevOBDData, assertMsg, gsi):
            gsi.update(obdData, prevOBDData)
            assert gsi.dotDispCnt == 0, assertMsg

        @pytest.mark.parametrize('obdData, prevOBDData, expThrottleActive', [
            ({'rpm': 2000, 'speed': 0, 'throttle': 0}, {}, False),
            ({'rpm': 2000, 'speed': 0, 'throttle': 1}, {}, True),
            ({'rpm': 2000, 'speed': 0, 'throttle': 2}, {}, True),
            ({'rpm': 2000, 'speed': 0, 'throttle': 100}, {}, True)
        ])
        def test_throttleActive(
            self, obdData, prevOBDData, expThrottleActive, gsi
        ):
            gsi.update(obdData, prevOBDData)
            assert gsi.throttleActive == expThrottleActive

        @pytest.mark.parametrize('obdData, prevOBDData, expectedDotDispCnt', [
            # No Indication Dots
            # ----------------------------------
            (
                {'time': 10, 'rpm': 1449, 'speed': 30, 'throttle': 40,
                'alt': 10},
                {'time': 0, 'rpm': 1449, 'speed': 30, 'throttle': 40,
                'alt': 10},
                0
            ),
            # 1 Indication Dot
            # ----------------------------------
            (
                {'time': 10, 'rpm': 1500, 'speed': 30, 'throttle': 40,
                'alt': 10},
                {'time': 0, 'rpm': 1500, 'speed': 30, 'throttle': 40,
                'alt': 10},
                1
            ),
            (
                {'time': 10, 'rpm': 1501, 'speed': 30, 'throttle': 40,
                'alt': 10},
                {'time': 0, 'rpm': 1501, 'speed': 30, 'throttle': 40,
                'alt': 10},
                1
            ),
            # 2 Indication Dots
            # ----------------------------------
            (
                {'time': 10, 'rpm': 1666, 'speed': 30, 'throttle': 40,
                'alt': 10},
                {'time': 0, 'rpm': 1666, 'speed': 30, 'throttle': 40,
                'alt': 10},
                1
            ),
            (
                {'time': 10, 'rpm': 1667, 'speed': 30, 'throttle': 40,
                'alt': 10},
                {'time': 0, 'rpm': 1667, 'speed': 30, 'throttle': 40,
                'alt': 10},
                2
            ),
            (
                {'time': 10, 'rpm': 1668, 'speed': 30, 'throttle': 40,
                'alt': 10},
                {'time': 0, 'rpm': 1668, 'speed': 30, 'throttle': 40,
                'alt': 10},
                2
            ),
            # 3 Indication Dots
            # ----------------------------------
            (
                {'time': 10, 'rpm': 1833, 'speed': 30, 'throttle': 40,
                'alt': 10},
                {'time': 0, 'rpm': 1833, 'speed': 30, 'throttle': 40,
                'alt': 10},
                2
            ),
            (
                {'time': 10, 'rpm': 1834, 'speed': 30, 'throttle': 40,
                'alt': 10},
                {'time': 0, 'rpm': 1834, 'speed': 30, 'throttle': 40,
                'alt': 10},
                3
            ),
            (
                {'time': 10, 'rpm': 1834, 'speed': 30, 'throttle': 40,
                'alt': 10},
                {'time': 0, 'rpm': 1834, 'speed': 30, 'throttle': 40,
                'alt': 10},
                3
            ),
            # 4/All Indication Dots
            # ----------------------------------
            (
                {'time': 10, 'rpm': 1999, 'speed': 30, 'throttle': 40,
                'alt': 10},
                {'time': 0, 'rpm': 1999, 'speed': 30, 'throttle': 40,
                'alt': 10},
                3
            ),
            (
                {'time': 10, 'rpm': 2000, 'speed': 30, 'throttle': 40,
                'alt': 10},
                {'time': 0, 'rpm': 2000, 'speed': 30, 'throttle': 40,
                'alt': 10},
                4
            ),
            (
                {'time': 10, 'rpm': 2001, 'speed': 30, 'throttle': 40,
                'alt': 10},
                {'time': 0, 'rpm': 2001, 'speed': 30, 'throttle': 40,
                'alt': 10},
                4
            ),
            # Road gradient affects shift point
            # ----------------------------------
            (
                {'time': 10, 'rpm': 1600, 'speed': 57, 'throttle': 40,
                'alt': 20},
                {'time': 0, 'rpm': 1600, 'speed': 57, 'throttle': 40,
                'alt': 10},
                0
            ),
            (
                {'time': 10, 'rpm': 2000, 'speed': 70, 'throttle': 40,
                'alt': 20},
                {'time': 0, 'rpm': 1800, 'speed': 60, 'throttle': 40,
                'alt': 10},
                1
            ),
            (
                {'time': 10, 'rpm': 2200, 'speed': 70, 'throttle': 40,
                'alt': 20},
                {'time': 0, 'rpm': 1800, 'speed': 60, 'throttle': 40,
                'alt': 10},
                2
            ),
            (
                {'time': 10, 'rpm': 2355, 'speed': 70, 'throttle': 40,
                'alt': 20},
                {'time': 0, 'rpm': 1800, 'speed': 60, 'throttle': 40,
                'alt': 10},
                3
            ),
            (
                {'time': 10, 'rpm': 2500, 'speed': 70, 'throttle': 40,
                'alt': 20},
                {'time': 0, 'rpm': 1800, 'speed': 60, 'throttle': 40,
                'alt': 10},
                4
            )
        ])
        def test_baseCase(self, obdData, prevOBDData, expectedDotDispCnt, gsi):
            gsi.update(obdData, prevOBDData)
            assert gsi.dotDispCnt == expectedDotDispCnt
