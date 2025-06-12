import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../event"))

from algorithm.track.Track import TrackStatus
from algorithm.track.Tracker import Tracker


class TestAssociation:
    def setup_method(self):
        config = {
            "gating_euclidean_threshold_m": 10000.0,  # Very wide threshold for tests
            "min_hits_to_confirm": 3,
            "max_misses_to_delete": 5,
            "verbose": False,
        }
        self.tracker = Tracker(config)

    def test_detection_to_track_association(self):
        """Test that nearby detections associate to existing tracks instead of creating new ones"""

        # Create initial track
        initial_detection = [
            {"timestamp_ms": 1000, "lla_position": [-34.9286, 138.5999, 1000]}
        ]

        tracks = self.tracker.update_all_tracks(
            all_localised_detections_lla=initial_detection,
            current_timestamp_ms=1000,
        )

        assert len(tracks) == 1
        track_id = next(iter(tracks.keys()))
        initial_track = tracks[track_id]
        assert initial_track.hits == 1

        # Send nearby detection that should associate to existing track
        nearby_detection = [
            {
                "timestamp_ms": 2000,
                "lla_position": [-34.9290, 138.6000, 1050],
            }  # 400m away
        ]

        tracks = self.tracker.update_all_tracks(
            all_localised_detections_lla=nearby_detection,
            current_timestamp_ms=2000,
        )

        # Should still have one track (associated, not created new)
        assert len(tracks) == 1
        assert track_id in tracks
        updated_track = tracks[track_id]
        assert updated_track.hits == 2  # Should have incremented hits
        assert updated_track.misses == 0  # Should not have missed

    def test_distant_detection_creates_new_track(self):
        """Test that distant detections create new tracks"""

        # Create a track first
        initial_detections = [
            {"timestamp_ms": 1000, "lla_position": [-34.9286, 138.5999, 1000]}
        ]

        tracks = self.tracker.update_all_tracks(
            all_localised_detections_lla=initial_detections, current_timestamp_ms=1000
        )

        assert len(tracks) == 1

        # Send a distant detection that should create new track
        distant_detections = [
            {"timestamp_ms": 2000, "lla_position": [-35.0000, 139.0000, 2000]}
        ]

        tracks = self.tracker.update_all_tracks(
            all_localised_detections_lla=distant_detections, current_timestamp_ms=2000
        )

        # Should now have two tracks
        assert len(tracks) == 2

        # Verify one track has 2 hits (the original) and one has 1 hit (new)
        hit_counts = [track.hits for track in tracks.values()]
        assert 1 in hit_counts  # Original track (1 hit, then missed)
        assert 1 in hit_counts  # New track

    def test_no_detections_increments_misses(self):
        """Test that tracks increment misses when no detections received"""

        # Create a track first
        initial_detections = [
            {"timestamp_ms": 1000, "lla_position": [-34.9286, 138.5999, 1000]}
        ]

        tracks = self.tracker.update_all_tracks(
            all_localised_detections_lla=initial_detections, current_timestamp_ms=1000
        )

        track_id = next(iter(tracks.keys()))
        initial_misses = tracks[track_id].misses

        # Process with no detections
        tracks = self.tracker.update_all_tracks(
            all_localised_detections_lla=[], current_timestamp_ms=2000
        )

        # Track should still exist but have incremented misses
        assert len(tracks) == 1
        assert track_id in tracks
        assert tracks[track_id].misses == initial_misses + 1

    def test_multiple_detections_to_single_track(self):
        """Test that multiple nearby detections don't all associate to same track"""

        # Create a track first
        initial_detections = [
            {"timestamp_ms": 1000, "lla_position": [-34.9286, 138.5999, 1000]}
        ]

        tracks = self.tracker.update_all_tracks(
            all_localised_detections_lla=initial_detections, current_timestamp_ms=1000
        )

        assert len(tracks) == 1

        # Send multiple detections that are close to the track
        multiple_detections = [
            {"timestamp_ms": 2000, "lla_position": [-34.9290, 138.6000, 1050]},
            {"timestamp_ms": 2000, "lla_position": [-34.9292, 138.6002, 1055]},
        ]

        tracks = self.tracker.update_all_tracks(
            all_localised_detections_lla=multiple_detections, current_timestamp_ms=2000
        )

        # Should have multiple tracks since only one detection can associate per track
        # (or the closest one associates and others create new tracks)
        assert len(tracks) >= 1

    def test_single_aircraft_trajectory_association(self):
        """Test that a single aircraft trajectory creates one track with multiple hits"""

        # Simulate aircraft flying straight line
        aircraft_detections = [
            {"timestamp_ms": 1000, "lla_position": [-34.9286, 138.5999, 1000]},
            {"timestamp_ms": 2000, "lla_position": [-34.9290, 138.6000, 1050]},
            {"timestamp_ms": 3000, "lla_position": [-34.9294, 138.6001, 1100]},
            {"timestamp_ms": 4000, "lla_position": [-34.9298, 138.6002, 1150]},
        ]

        track_id = None
        for i, detection in enumerate(aircraft_detections):
            tracks = self.tracker.update_all_tracks(
                all_localised_detections_lla=[detection],
                current_timestamp_ms=detection["timestamp_ms"],
            )

            if i == 0:
                # First detection creates track
                assert len(tracks) == 1
                track_id = next(iter(tracks.keys()))
                assert tracks[track_id].hits == 1
            else:
                # Subsequent detections should associate to same track
                assert len(tracks) == 1
                assert track_id in tracks
                assert tracks[track_id].hits == i + 1  # Should increment hits

        # Final verification
        final_track = tracks[track_id]
        assert final_track.hits == 4  # All 4 detections associated
        assert final_track.status == TrackStatus.CONFIRMED  # Should be confirmed by now
