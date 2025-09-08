import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../event"))

from algorithm.geometry.Geometry import Geometry


class TestGeometry:
    def test_lla2enu(self):
        # Test case 1: Same point should be at origin
        result = Geometry.lla2enu(-34.9286, 138.5999, 50, -34.9286, 138.5999, 50)
        assert abs(result[0]) < 0.001
        assert abs(result[1]) < 0.001
        assert abs(result[2]) < 0.001

        # Test case 2: Point to the east
        result = Geometry.lla2enu(-34.9286, 139.0, 50, -34.9286, 138.5999, 50)
        assert result[0] > 0  # East is positive
        assert abs(result[1]) < 1  # North should be close to 0
        assert abs(result[2]) < 0.001  # Same altitude

    def test_enu2lla(self):
        # Test case 1: Origin should return reference point
        result = Geometry.enu2lla(0, 0, 0, -34.9286, 138.5999, 50)
        assert abs(result[0] - (-34.9286)) < 0.0001
        assert abs(result[1] - 138.5999) < 0.0001
        assert abs(result[2] - 50) < 0.001

        # Test case 2: Point 1000m east
        result = Geometry.enu2lla(1000, 0, 0, -34.9286, 138.5999, 50)
        assert abs(result[0] - (-34.9286)) < 0.0001  # Latitude unchanged
        assert result[1] > 138.5999  # Longitude increases eastward
        assert abs(result[2] - 50) < 0.001

    def test_distance_enu(self):
        # Test case 1: Distance between same points
        result = Geometry.distance_enu((0, 0, 0), (0, 0, 0))
        assert abs(result) < 0.001

        # Test case 2: Distance in 3D space
        result = Geometry.distance_enu((0, 0, 0), (3, 4, 0))
        assert abs(result - 5) < 0.001  # 3-4-5 triangle

        # Test case 3: 3D distance
        result = Geometry.distance_enu((0, 0, 0), (1, 1, 1))
        assert abs(result - 1.732) < 0.01  # sqrt(3)

    def test_distance_lla(self):
        # Test case 1: Distance between same points
        result = Geometry.distance_lla(
            (-34.9286, 138.5999, 50),
            (-34.9286, 138.5999, 50)
        )
        assert abs(result) < 0.001

        # Test case 2: Distance between two different points
        result = Geometry.distance_lla(
            (-34.9286, 138.5999, 50),
            (-34.9286, 138.6099, 50)
        )
        assert result > 0  # Should be positive distance

    def test_average_points(self):
        # Test case 1: Average of single point
        result = Geometry.average_points([(1, 2, 3)])
        assert result == [1, 2, 3]

        # Test case 2: Average of multiple points
        result = Geometry.average_points([(0, 0, 0), (2, 2, 2)])
        assert result == [1, 1, 1]

        # Test case 3: Average of three points
        result = Geometry.average_points([(1, 1, 1), (2, 2, 2), (3, 3, 3)])
        assert result == [2, 2, 2]