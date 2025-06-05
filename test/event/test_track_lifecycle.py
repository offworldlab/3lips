import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../event"))


import numpy as np
from algorithm.track.Track import Track, TrackStatus


class TestTrackLifecycle:
    def test_track_states(self):
        """Test that tracks move through states correctly:
        TENTATIVE → CONFIRMED → COASTING → DELETED"""

        # Create a tentative track
        initial_detection = {
            "timestamp_ms": 1000,
            "lla_position": [-34.9286, 138.5999, 1000],
        }
        track = Track(
            initial_detection=initial_detection,
            timestamp_ms=1000,
            status=TrackStatus.TENTATIVE,
        )

        # Initially tentative
        assert track.status == TrackStatus.TENTATIVE
        assert track.hits == 1
        assert track.misses == 0

        # Update track multiple times to confirm it
        for i in range(3):
            new_state = np.array(
                [1000 + i * 10, 2000 + i * 10, 3000 + i * 10, 10, 10, 10]
            )
            new_covariance = np.eye(6) * 100
            track.update(
                detection={"timestamp_ms": 1000 + i * 1000, "test": True},
                timestamp_ms=1000 + i * 1000,
                new_state=new_state,
                new_covariance=new_covariance,
            )

        # Should be confirmed after enough hits
        assert track.status == TrackStatus.CONFIRMED
        assert track.hits >= 3

        # Miss the track several times to make it coast
        for _ in range(4):
            track.increment_misses()
            track.increment_age()

        # Should be coasting after enough misses
        assert track.status == TrackStatus.COASTING
        assert track.misses > 3

    def test_adsb_track_starts_confirmed(self):
        """Test that ADS-B tracks start as CONFIRMED"""
        adsb_info = {"hex": "ABC123", "flight": "TEST01"}
        initial_detection = {
            "timestamp_ms": 1000,
            "lla_position": [-34.9286, 138.5999, 1000],
            "adsb_info": adsb_info,
        }

        track = Track(
            initial_detection=initial_detection,
            timestamp_ms=1000,
            status=TrackStatus.CONFIRMED,
            adsb_info=adsb_info,
        )

        # ADS-B tracks start confirmed
        assert track.status == TrackStatus.CONFIRMED
        assert track.adsb_info == adsb_info
        assert track.adsb_info["hex"] == "ABC123"

    def test_track_update_increments_counters(self):
        """Test that track updates increment hits and reset misses"""
        track = Track(
            initial_detection={"timestamp_ms": 1000},
            timestamp_ms=1000,
            status=TrackStatus.TENTATIVE,
        )

        initial_hits = track.hits

        # Update track
        new_state = np.array([1000, 2000, 3000, 10, 10, 10])
        new_covariance = np.eye(6) * 100
        track.update(
            detection={"timestamp_ms": 2000},
            timestamp_ms=2000,
            new_state=new_state,
            new_covariance=new_covariance,
        )

        # Hits should increment, misses should reset
        assert track.hits == initial_hits + 1
        assert track.misses == 0

    def test_track_miss_increments_counters(self):
        """Test that track misses increment miss counter"""
        track = Track(
            initial_detection={"timestamp_ms": 1000},
            timestamp_ms=1000,
            status=TrackStatus.CONFIRMED,
        )

        initial_misses = track.misses

        # Miss the track
        track.increment_misses()

        # Misses should increment
        assert track.misses == initial_misses + 1
