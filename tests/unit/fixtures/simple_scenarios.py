"""Simple test scenarios for tracking tests."""

SINGLE_AIRCRAFT = {
    "detections": [
        {"timestamp_ms": 1000, "lla_position": [-34.9286, 138.5999, 1000]},
        {"timestamp_ms": 2000, "lla_position": [-34.9290, 138.6000, 1050]},
        {"timestamp_ms": 3000, "lla_position": [-34.9294, 138.6001, 1100]},
    ],
    "expected_track_count": 1,
    "expected_final_altitude": 1100,
}

ADSB_AIRCRAFT = {
    "adsb_info": {"hex": "ABC123", "flight": "TEST01"},
    "detections": [
        {
            "timestamp_ms": 1000,
            "lla_position": [-34.9286, 138.5999, 2000],
            "adsb_info": {"hex": "ABC123", "flight": "TEST01"},
        },
        {
            "timestamp_ms": 2000,
            "lla_position": [-34.9290, 138.6000, 2050],
            "adsb_info": {"hex": "ABC123", "flight": "TEST01"},
        },
    ],
    "expected_track_count": 1,
    "expected_status": "CONFIRMED",
}

TWO_AIRCRAFT = {
    "detections": [
        # Aircraft 1
        {"timestamp_ms": 1000, "lla_position": [-34.9286, 138.5999, 1000]},
        {"timestamp_ms": 2000, "lla_position": [-34.9290, 138.6000, 1050]},
        # Aircraft 2 (far away)
        {"timestamp_ms": 1000, "lla_position": [-35.0000, 139.0000, 2000]},
        {"timestamp_ms": 2000, "lla_position": [-35.0010, 139.0010, 2050]},
    ],
    "expected_track_count": 2,
}
