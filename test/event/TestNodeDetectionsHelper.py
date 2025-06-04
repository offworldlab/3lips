import unittest
from unittest.mock import patch

import numpy as np

from event.algorithm.associator.NodeDetectionsHelper import NodeDetectionsHelper


class MockTrack:
    def __init__(self, state_vector):
        self.state_vector = np.array(state_vector)


class TestNodeDetectionsHelper(unittest.TestCase):
    def setUp(self):
        self.helper = NodeDetectionsHelper()

    @patch("event.algorithm.geometry.Geometry.Geometry.lla2ecef")
    def test_has_existing_tracks_in_detection_space_true(self, mock_lla2ecef):
        # Setup
        mock_lla2ecef.return_value = (1000, 2000, 3000)
        new_detection_lla = [1, 2, 3]
        existing_tracks_map = {
            "track1": MockTrack([1001, 2001, 3001, 0, 0, 0]),
            "track2": MockTrack([5000, 6000, 7000, 0, 0, 0]),
        }
        gating_threshold_m = 5
        # Should be within threshold for track1
        result = self.helper.has_existing_tracks_in_detection_space(
            new_detection_lla,
            existing_tracks_map,
            gating_threshold_m,
        )
        self.assertTrue(result)

    @patch("event.algorithm.geometry.Geometry.Geometry.lla2ecef")
    def test_has_existing_tracks_in_detection_space_false(self, mock_lla2ecef):
        mock_lla2ecef.return_value = (0, 0, 0)
        new_detection_lla = [1, 2, 3]
        existing_tracks_map = {"track1": MockTrack([1000, 2000, 3000, 0, 0, 0])}
        gating_threshold_m = 10
        # Should be outside threshold
        result = self.helper.has_existing_tracks_in_detection_space(
            new_detection_lla,
            existing_tracks_map,
            gating_threshold_m,
        )
        self.assertFalse(result)

    def test_has_existing_tracks_in_detection_space_empty(self):
        new_detection_lla = [1, 2, 3]
        existing_tracks_map = {}
        gating_threshold_m = 10
        result = self.helper.has_existing_tracks_in_detection_space(
            new_detection_lla,
            existing_tracks_map,
            gating_threshold_m,
        )
        self.assertFalse(result)

    @patch("event.algorithm.geometry.Geometry.Geometry.lla2ecef")
    def test__get_node_rx_ecef_valid(self, mock_lla2ecef):
        mock_lla2ecef.return_value = (1, 2, 3)
        node_config = {
            "location": {"rx": {"latitude": 10, "longitude": 20, "altitude": 30}},
        }
        result = self.helper._get_node_rx_ecef(node_config)
        np.testing.assert_array_equal(result, np.array([1, 2, 3]))

    def test__get_node_rx_ecef_invalid(self):
        # Missing location
        node_config = {}
        result = self.helper._get_node_rx_ecef(node_config)
        self.assertIsNone(result)
        # Missing rx
        node_config = {"location": {}}
        result = self.helper._get_node_rx_ecef(node_config)
        self.assertIsNone(result)

    @patch("event.algorithm.geometry.Geometry.Geometry.lla2ecef")
    def test_get_nodes_with_overlapping_detection_space(self, mock_lla2ecef):
        # Setup two nodes within range, one out of range
        mock_lla2ecef.side_effect = [
            (0, 0, 0),  # current node
            (1, 1, 1),  # node2 (close)
            (100, 100, 100),  # node3 (far)
        ]
        all_nodes_data = {
            "node1": {
                "config": {
                    "location": {"rx": {"latitude": 0, "longitude": 0, "altitude": 0}},
                },
            },
            "node2": {
                "config": {
                    "location": {"rx": {"latitude": 1, "longitude": 1, "altitude": 1}},
                },
            },
            "node3": {
                "config": {
                    "location": {
                        "rx": {"latitude": 100, "longitude": 100, "altitude": 100},
                    },
                },
            },
        }
        max_effective_range_m = 2
        result = self.helper.get_nodes_with_overlapping_detection_space(
            "node1",
            all_nodes_data,
            max_effective_range_m,
        )
        self.assertIn("node2", result)
        self.assertNotIn("node3", result)
        self.assertNotIn("node1", result)

    @patch("event.algorithm.geometry.Geometry.Geometry.lla2ecef")
    def test_get_nodes_with_overlapping_detection_space_missing_config(
        self,
        mock_lla2ecef,
    ):
        all_nodes_data = {
            "node1": {
                "config": {
                    "location": {"rx": {"latitude": 0, "longitude": 0, "altitude": 0}},
                },
            },
            "node2": {},  # Missing config
        }
        max_effective_range_m = 2
        result = self.helper.get_nodes_with_overlapping_detection_space(
            "node1",
            all_nodes_data,
            max_effective_range_m,
        )
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
