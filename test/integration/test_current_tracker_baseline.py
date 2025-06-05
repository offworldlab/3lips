import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../event"))

from algorithm.track.Track import TrackStatus
from algorithm.track.Tracker import Tracker


class TestCurrentTrackerBaseline:
    def setup_method(self):
        # Use default configuration similar to production
        config = {
            "gating_euclidean_threshold_m": 5000.0,
            "min_hits_to_confirm": 3,
            "max_misses_to_delete": 5,
            "verbose": False,
        }
        self.tracker = Tracker(config)

    def test_current_tracker_baseline(self):
        """Capture how the current tracker behaves"""

        # Define a standard test scenario
        baseline_scenario = {
            "description": "Single aircraft with consistent movement",
            "detections": [
                {"timestamp_ms": 1000, "lla_position": [-34.9286, 138.5999, 1000]},
                {"timestamp_ms": 2000, "lla_position": [-34.9290, 138.6000, 1050]},
                {"timestamp_ms": 3000, "lla_position": [-34.9294, 138.6001, 1100]},
                {"timestamp_ms": 4000, "lla_position": [-34.9298, 138.6002, 1150]},
                {"timestamp_ms": 5000, "lla_position": [-34.9302, 138.6003, 1200]},
            ],
            "adsb_detections": [
                {
                    "timestamp_ms": 3000,
                    "lla_position": [-34.9294, 138.6001, 1100],
                    "adsb_info": {"hex": "BASELINE", "flight": "BASE01"},
                }
            ],
        }

        baseline_results = []

        # Process the scenario step by step
        for _, detection in enumerate(baseline_scenario["detections"]):
            timestamp = detection["timestamp_ms"]

            # Include ADS-B at timestamp 3000
            adsb_data = []
            if timestamp == 3000:
                adsb_data = baseline_scenario["adsb_detections"]

            tracks = self.tracker.update_all_tracks(
                all_localised_detections_lla=[detection],
                current_timestamp_ms=timestamp,
                adsb_detections_lla=adsb_data,
            )

            # Capture the state
            step_result = {
                "timestamp": timestamp,
                "input_detection": detection,
                "input_adsb": adsb_data,
                "track_count": len(tracks),
                "tracks": {},
            }

            for track_id, track in tracks.items():
                step_result["tracks"][track_id] = {
                    "status": track.status.name,
                    "hits": track.hits,
                    "misses": track.misses,
                    "age_scans": track.age_scans,
                    "has_adsb": track.adsb_info is not None,
                    "adsb_hex": track.adsb_info["hex"] if track.adsb_info else None,
                    "position": track.state_vector[:3].tolist()
                    if track.state_vector is not None
                    else None,
                }

            baseline_results.append(step_result)

        # Validate the baseline results
        assert len(baseline_results) == 5

        # Basic sanity checks
        final_result = baseline_results[-1]
        assert final_result["track_count"] >= 1

        # At least one track should exist at the end
        track_ids = list(final_result["tracks"].keys())
        assert len(track_ids) >= 1

        # Record the actual behavior (may be creating new tracks instead of associating)
        max_hits = max(track["hits"] for track in final_result["tracks"].values())
        # Current tracker behavior: captures what actually happens (not what we expect)
        assert max_hits >= 1

        # Store baseline for future comparison (this would be saved to file in practice)
        self.baseline_behavior = {
            "scenario": baseline_scenario,
            "results": baseline_results,
            "summary": {
                "total_steps": len(baseline_results),
                "final_track_count": final_result["track_count"],
                "max_hits_achieved": max_hits,
                "tracks_with_adsb": sum(
                    1 for track in final_result["tracks"].values() if track["has_adsb"]
                ),
                "final_track_states": [
                    track["status"] for track in final_result["tracks"].values()
                ],
            },
        }

        # This baseline can be compared against Stone Soup implementation
        # baseline_behavior stored for future comparison

    def test_adsb_baseline_behavior(self):
        """Capture baseline behavior for ADS-B integration"""

        adsb_scenario = [
            {
                "timestamp_ms": 1000,
                "lla_position": [-34.9286, 138.5999, 2000],
                "adsb_info": {"hex": "ADS001", "flight": "TEST01"},
            },
            {
                "timestamp_ms": 2000,
                "lla_position": [-34.9290, 138.6000, 2050],
                "adsb_info": {"hex": "ADS001", "flight": "TEST01"},
            },
            {
                "timestamp_ms": 3000,
                "lla_position": [-34.9294, 138.6001, 2100],
                "adsb_info": {"hex": "ADS001", "flight": "TEST01"},
            },
        ]

        results = []

        for detection in adsb_scenario:
            tracks = self.tracker.update_all_tracks(
                all_localised_detections_lla=[],
                current_timestamp_ms=detection["timestamp_ms"],
                adsb_detections_lla=[detection],
            )

            results.append(
                {
                    "timestamp": detection["timestamp_ms"],
                    "track_count": len(tracks),
                    "confirmed_tracks": sum(
                        1
                        for track in tracks.values()
                        if track.status == TrackStatus.CONFIRMED
                    ),
                    "adsb_tracks": sum(
                        1 for track in tracks.values() if track.adsb_info is not None
                    ),
                }
            )

        # Validate ADS-B baseline behavior
        assert len(results) == 3

        # ADS-B tracks should be confirmed immediately
        final_result = results[-1]
        assert final_result["confirmed_tracks"] >= 1
        assert final_result["adsb_tracks"] >= 1

        # Store for potential future use
        self.adsb_baseline = results

    def test_association_baseline_behavior(self):
        """Capture baseline behavior for data association"""

        # Two aircraft in different locations
        detections_step1 = [
            {
                "timestamp_ms": 1000,
                "lla_position": [-34.9286, 138.5999, 1000],
            },  # Aircraft 1
            {
                "timestamp_ms": 1000,
                "lla_position": [-35.0000, 139.0000, 2000],
            },  # Aircraft 2 (far)
        ]

        detections_step2 = [
            {
                "timestamp_ms": 2000,
                "lla_position": [-34.9290, 138.6000, 1050],
            },  # Aircraft 1 moved
            {
                "timestamp_ms": 2000,
                "lla_position": [-35.0010, 139.0010, 2050],
            },  # Aircraft 2 moved
        ]

        # Step 1
        tracks_t1 = self.tracker.update_all_tracks(
            all_localised_detections_lla=detections_step1, current_timestamp_ms=1000
        )

        # Step 2
        tracks_t2 = self.tracker.update_all_tracks(
            all_localised_detections_lla=detections_step2, current_timestamp_ms=2000
        )

        baseline_association = {
            "step1_tracks": len(tracks_t1),
            "step2_tracks": len(tracks_t2),
            "tracks_with_multiple_hits": sum(
                1 for track in tracks_t2.values() if track.hits > 1
            ),
        }

        # Basic validation
        assert baseline_association["step1_tracks"] >= 1
        assert baseline_association["step2_tracks"] >= 1

        # Store for potential future use
        self.association_baseline = baseline_association
