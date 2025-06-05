import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../event"))

from algorithm.track.Track import TrackStatus
from algorithm.track.Tracker import Tracker


class TestAdsbIntegration:
    def setup_method(self):
        config = {
            "gating_euclidean_threshold_m": 1000.0,
            "min_hits_to_confirm": 3,
            "max_misses_to_delete": 5,
            "verbose": False,
        }
        self.tracker = Tracker(config)

    def test_adsb_track_creation(self):
        """Test that ADS-B data creates confirmed tracks"""

        adsb_detections = [
            {
                "timestamp_ms": 1000,
                "lla_position": [-34.9286, 138.5999, 2000],
                "adsb_info": {"hex": "ABC123", "flight": "TEST01"},
            }
        ]

        tracks = self.tracker.update_all_tracks(
            all_localised_detections_lla=[],  # No radar detections
            current_timestamp_ms=1000,
            adsb_detections_lla=adsb_detections,
        )

        # Should have created one confirmed track
        assert len(tracks) == 1
        track = next(iter(tracks.values()))
        assert track.status == TrackStatus.CONFIRMED
        assert track.adsb_info is not None
        assert track.adsb_info["hex"] == "ABC123"
        assert track.adsb_info["flight"] == "TEST01"

    def test_adsb_updates_existing_track(self):
        """Test that ADS-B data can update existing radar tracks"""

        # Create radar track first
        radar_detections = [
            {"timestamp_ms": 1000, "lla_position": [-34.9286, 138.5999, 1000]}
        ]

        tracks = self.tracker.update_all_tracks(
            all_localised_detections_lla=radar_detections, current_timestamp_ms=1000
        )

        assert len(tracks) == 1
        track_id = next(iter(tracks.keys()))
        initial_track = tracks[track_id]
        assert initial_track.status == TrackStatus.TENTATIVE
        assert initial_track.adsb_info is None

        # Now send ADS-B data for nearby position
        adsb_detections = [
            {
                "timestamp_ms": 2000,
                "lla_position": [-34.9290, 138.6000, 1050],
                "adsb_info": {"hex": "ABC123", "flight": "TEST01"},
            }
        ]

        tracks = self.tracker.update_all_tracks(
            all_localised_detections_lla=[],
            current_timestamp_ms=2000,
            adsb_detections_lla=adsb_detections,
        )

        # Should still have the same track, now with ADS-B info
        # (or could be a new confirmed track, depending on association distance)
        assert len(tracks) >= 1

        # Check if existing track was updated or new confirmed track created
        has_adsb_track = any(
            track.adsb_info is not None and track.adsb_info["hex"] == "ABC123"
            for track in tracks.values()
        )
        assert has_adsb_track

    def test_multiple_adsb_aircraft(self):
        """Test multiple ADS-B aircraft create separate tracks"""

        adsb_detections = [
            {
                "timestamp_ms": 1000,
                "lla_position": [-34.9286, 138.5999, 2000],
                "adsb_info": {"hex": "ABC123", "flight": "TEST01"},
            },
            {
                "timestamp_ms": 1000,
                "lla_position": [-35.0000, 139.0000, 3000],
                "adsb_info": {"hex": "DEF456", "flight": "TEST02"},
            },
        ]

        tracks = self.tracker.update_all_tracks(
            all_localised_detections_lla=[],
            current_timestamp_ms=1000,
            adsb_detections_lla=adsb_detections,
        )

        # Should have two confirmed tracks
        assert len(tracks) == 2

        # Both should be confirmed with different hex codes
        hex_codes = [track.adsb_info["hex"] for track in tracks.values()]
        assert "ABC123" in hex_codes
        assert "DEF456" in hex_codes

        for track in tracks.values():
            assert track.status == TrackStatus.CONFIRMED

    def test_adsb_track_persists_without_updates(self):
        """Test that ADS-B tracks handle missing updates gracefully"""

        # Create ADS-B track
        adsb_detections = [
            {
                "timestamp_ms": 1000,
                "lla_position": [-34.9286, 138.5999, 2000],
                "adsb_info": {"hex": "ABC123", "flight": "TEST01"},
            }
        ]

        tracks = self.tracker.update_all_tracks(
            all_localised_detections_lla=[],
            current_timestamp_ms=1000,
            adsb_detections_lla=adsb_detections,
        )

        track_id = next(iter(tracks.keys()))
        initial_misses = tracks[track_id].misses

        # Process several cycles without ADS-B updates
        for i in range(3):
            tracks = self.tracker.update_all_tracks(
                all_localised_detections_lla=[],
                current_timestamp_ms=2000 + i * 1000,
                adsb_detections_lla=[],
            )

        # Track should still exist but have accumulated misses
        assert len(tracks) == 1
        assert track_id in tracks
        assert tracks[track_id].misses > initial_misses
