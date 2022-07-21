import pytest
import device  # noqa: F401
import utils


# kmhToMps
# -----------------------------------
@pytest.mark.parametrize('kmh, expectedMps', [
    (0, 0),
    (1, 0.2777777777777778),
    (40, 11.11111111111111),
    (-10, -2.7777777777777777)
])
def test_kmhToMps(kmh, expectedMps):
    assert utils.kmhToMps(kmh) == expectedMps
