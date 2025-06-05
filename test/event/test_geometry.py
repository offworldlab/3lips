import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../event"))

from algorithm.geometry.Geometry import Geometry


class TestGeometry:
    def test_lla2ecef(self):
        # test case 1
        result = Geometry.lla2ecef(-34.9286, 138.5999, 50)
        assert abs(result[0] - (-3926830.77177051)) < 0.001
        assert abs(result[1] - 3461979.19806774) < 0.001
        assert abs(result[2] - (-3631404.11418915)) < 0.001

        # test case 2
        result = Geometry.lla2ecef(0, 0, 0)
        assert abs(result[0] - 6378137.0) < 0.001
        assert abs(result[1] - 0) < 0.001
        assert abs(result[2] - 0) < 0.001

    def test_ecef2lla(self):
        # test case 1
        result = Geometry.ecef2lla(
            -3926830.77177051,
            3461979.19806774,
            -3631404.11418915,
        )
        assert abs(result[0] - (-34.9286)) < 0.0001
        assert abs(result[1] - 138.5999) < 0.0001
        assert abs(result[2] - 50) < 0.001

        # test case 2
        result = Geometry.ecef2lla(6378137.0, 0, 0)
        assert abs(result[0] - 0) < 0.0001
        assert abs(result[1] - 0) < 0.0001
        assert abs(result[2] - 0) < 0.001

    def test_enu2ecef(self):
        # test case 1
        result = Geometry.enu2ecef(0, 0, 0, -34.9286, 138.5999, 50)
        assert abs(result[0] - (-3926830.77177051)) < 0.001
        assert abs(result[1] - 3461979.19806774) < 0.001
        assert abs(result[2] - (-3631404.11418915)) < 0.001

        # test case 2
        result = Geometry.enu2ecef(-1000, 2000, 3000, -34.9286, 138.5999, 50)
        assert abs(result[0] - (-3928873.3865007)) < 0.001
        assert abs(result[1] - 3465113.14948365) < 0.001
        assert abs(result[2] - (-3631482.0474089)) < 0.001
