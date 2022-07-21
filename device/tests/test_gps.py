import pytest
from freezegun import freeze_time
from datetime import datetime
import device  # noqa: F401
import gps


def roundCoords(coords, ndigits=0):
    return {
        'latitude': round(coords['latitude'], ndigits),
        'longitude': round(coords['longitude'], ndigits)
    }


class Test_getGPSCoords:
    @pytest.mark.parametrize('timeIntvl, expectedLat, expectedLng', [
        (0, 5, 10),
        (1, 15, 30),
        (2, 25, 50),
        (3, 7.5, 15),
        (3.99, -10, -20),
        (4, 5, 10),
        (5, 15, 30),
        (6, 25, 50),
        (7, 7.5, 15),
        (7.99, -10, -20)
    ])
    def test_timeIntvlInterpolation(self, timeIntvl, expectedLat, expectedLng):
        with freeze_time(datetime.fromtimestamp(gps.startTime + timeIntvl)):
            assert roundCoords(gps.getGPSCoords()) == {
                'latitude': round(expectedLat),
                'longitude': round(expectedLng)
            }
