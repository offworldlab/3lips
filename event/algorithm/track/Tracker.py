from datetime import datetime

import numpy as np
from stonesoup.types.state import State

from ..geometry.Geometry import Geometry

# Import Stone Soup tracker implementation
from .StoneSoupTracker import StoneSoupTracker
from .Track import Track, TrackStatus


class Tracker:
    """@class Tracker
    @brief Manages a list of active tracks using Stone Soup algorithms.
    """

    def __init__(self, config=None):
        """@brief Constructor for the Tracker class.
        @param config (dict, optional): Configuration dictionary for the tracker.
        """
        # --- Default Configuration ---
        # These can be overridden by the 'config' parameter passed during instantiation
        self.config = {
            "max_misses_to_delete": 5,  # Max consecutive scans a track can be missed before deletion
            "min_hits_to_confirm": 3,  # Min hits required to change a track from TENTATIVE to CONFIRMED
            "gating_euclidean_threshold_m": 5000.0,  # Euclidean distance threshold for gating (in meters)
            "gating_mahalanobis_threshold": 11.345,  # Chi-squared for 3DOF (x,y,z), P_G=0.99
            # Initial uncertainty for new tracks (standard deviations)
            "initial_pos_uncertainty_ecef_m": [100.0, 100.0, 100.0],  # x,y,z ECEF
            "initial_vel_uncertainty_ecef_mps": [50.0, 50.0, 50.0],  # vx,vy,vz ECEF
            "dt_default_s": 1.0,  # Default time step in seconds if not calculable
            "process_noise_coeff": 0.1,  # Stone Soup process noise coefficient
            "measurement_noise_coeff": 500.0,  # Stone Soup measurement noise coefficient
            "verbose": False,
            "use_stone_soup": True,  # Enable Stone Soup by default
        }
        if config:
            self.config.update(config)

        # Initialize Stone Soup tracker or fallback to legacy implementation
        if self.config.get("use_stone_soup", True):
            try:
                self.stone_soup_tracker = StoneSoupTracker(self.config)
                self.active_tracks = self.stone_soup_tracker.active_tracks
                self.last_timestamp_ms = None
                if self.config["verbose"]:
                    print("Tracker initialized with Stone Soup backend")
            except Exception as e:
                if self.config["verbose"]:
                    print(f"Warning: Failed to initialize Stone Soup tracker ({e}), falling back to legacy implementation")
                self.stone_soup_tracker = None
                self._init_legacy_tracker()
        else:
            self.stone_soup_tracker = None
            self._init_legacy_tracker()

    def _init_legacy_tracker(self):
        """Initialize legacy tracker implementation."""
        self.active_tracks = {}  # Dictionary to store active tracks, keyed by track_id
        self.last_timestamp_ms = None  # Timestamp of the last update cycle
        
        if self.config["verbose"]:
            print("Tracker initialized with legacy backend")

    def _predict_tracks(self, dt_seconds):
        """@brief Predicts the state of all active tracks to the current time.
        @param dt_seconds (float): Time delta since the last update.
        @return (dict): Map of {track_id: (predicted_state_ecef, predicted_covariance_ecef)}
        """
        predicted_map = {}
        for track_id, track in self.active_tracks.items():
            # The track.predict() method should update its internal state
            # and ideally return the predicted state and covariance.
            # Or, the filter object within the track would be directly manipulated.
            track.predict(
                dt_seconds,
            )  # This updates track.state_vector and track.covariance_matrix
            predicted_map[track_id] = (
                track.state_vector.copy(),
                track.covariance_matrix.copy(),
            )
            if self.config["verbose"]:
                print(f"Predicted Track {track_id}: State={track.state_vector[:3]}")
        return predicted_map

    def _convert_localised_detections_to_measurements(self, localised_detections_lla):
        """@brief Converts a list of localised LLA detections into a list of ECEF measurements
               with associated covariances for the tracker.
        @param localised_detections_lla (list): List of detection dicts, each with 'lla_position'.
        @return (list): List of tuples (measurement_ecef_pos, measurement_cov_ecef_pos, original_detection_data).
        """
        measurements = []
        for det_data in localised_detections_lla:
            try:
                lat, lon, alt = det_data["lla_position"]
                x_ecef, y_ecef, z_ecef = Geometry.lla2ecef(lat, lon, alt)
                measurement_pos_ecef = np.array([x_ecef, y_ecef, z_ecef])

                # Placeholder for measurement covariance in ECEF.
                # A proper implementation would transform LLA covariance (if available) to ECEF.
                # For now, using a diagonal matrix based on configured initial position uncertainty
                # as a proxy for measurement noise. This is a simplification.
                # This should ideally come from the sensor model or the localisation algorithm.
                std_devs = self.config[
                    "initial_pos_uncertainty_ecef_m"
                ]  # Re-using this for simplicity
                measurement_cov_ecef_pos = np.diag(np.array(std_devs) ** 2)

                measurements.append(
                    (measurement_pos_ecef, measurement_cov_ecef_pos, det_data),
                )
            except Exception as e:
                print(
                    f"Error converting detection to ECEF measurement: {det_data}, Error: {e}",
                )
                continue
        return measurements

    def _data_association(self, predicted_tracks_map, measurements):
        """@brief Associates measurements to predicted tracks using a simple gating and
               greedy nearest neighbor assignment.
        @param predicted_tracks_map (dict): {track_id: (predicted_state_ecef, predicted_covariance_ecef)}
        @param measurements (list): List of (measurement_ecef_pos, measurement_cov_ecef_pos, original_det_data)
        @return (tuple): (associations, unassociated_track_ids, unassociated_measurement_indices)
                         associations is {track_id: measurement_index}
        """
        associations = {}
        unassociated_track_ids = set(predicted_tracks_map.keys())
        unassociated_measurement_indices = set(range(len(measurements)))

        if not predicted_tracks_map or not measurements:
            return (
                associations,
                unassociated_track_ids,
                unassociated_measurement_indices,
            )

        track_ids_list = list(predicted_tracks_map.keys())
        num_tracks = len(track_ids_list)
        num_measurements = len(measurements)

        # Cost matrix: rows are tracks, columns are measurements
        cost_matrix = np.full((num_tracks, num_measurements), np.inf)
        gating_threshold_sq = self.config["gating_euclidean_threshold_m"] ** 2

        for i, track_id in enumerate(track_ids_list):
            predicted_state_ecef, _ = predicted_tracks_map[track_id]
            # Ensure track position is a 1D array for proper distance calculation
            track_pos_ecef = np.array(predicted_state_ecef[:3]).flatten()

            for j, (meas_pos_ecef, _, _) in enumerate(measurements):
                # Ensure measurement position is also 1D array
                meas_pos_ecef = np.array(meas_pos_ecef).flatten()

                # Euclidean distance for gating
                dist_sq = np.sum((track_pos_ecef - meas_pos_ecef) ** 2)

                if dist_sq < gating_threshold_sq:
                    cost_matrix[i, j] = np.sqrt(
                        dist_sq
                    )  # Store actual distance as cost

        # Greedy assignment (Nearest Neighbor based on smallest cost)
        # This is a simple approach; more robust methods (Hungarian, JPDA) exist.

        # Sort potential associations by cost to make greedy assignment
        possible_assignments = []
        for r in range(num_tracks):
            for c in range(num_measurements):
                if cost_matrix[r, c] != np.inf:
                    possible_assignments.append(
                        (cost_matrix[r, c], r, c),
                    )  # cost, track_idx, meas_idx

        possible_assignments.sort()  # Sort by cost (ascending)

        for cost, track_idx, meas_idx in possible_assignments:
            track_id = track_ids_list[track_idx]
            if (
                track_id in unassociated_track_ids
                and meas_idx in unassociated_measurement_indices
            ):
                associations[track_id] = meas_idx
                unassociated_track_ids.remove(track_id)
                unassociated_measurement_indices.remove(meas_idx)
                if self.config["verbose"]:
                    print(
                        f"Associated Track {track_id} with Measurement {meas_idx} (cost: {cost:.2f})",
                    )

        return associations, unassociated_track_ids, unassociated_measurement_indices

    def _initiate_new_track(
        self,
        measurement_pos_ecef,
        measurement_cov_ecef_pos,
        original_detection_data,
        timestamp_ms,
        status=TrackStatus.TENTATIVE,
    ):
        """@brief Initiates a new track from an unassociated measurement.
        @param status: Track status to initialize with (TENTATIVE for radar, CONFIRMED for ADS-B)
        """
        # Use UUID from Track class by default
        # track_id = self._generate_track_id() # Not needed if Track class handles UUID

        initial_vel_ecef = np.array([0.0, 0.0, 0.0])  # Assume zero initial velocity
        initial_state_ecef = np.concatenate((measurement_pos_ecef, initial_vel_ecef))

        # Initial covariance for the state vector [pos, vel]
        pos_cov_init = measurement_cov_ecef_pos * (
            self.config.get("initial_position_uncertainty_factor", 1.0) ** 2
        )

        vel_uncertainty_std = self.config["initial_vel_uncertainty_ecef_mps"]
        vel_cov_init_diag = (
            [s**2 for s in vel_uncertainty_std]
            if isinstance(vel_uncertainty_std, list)
            else [vel_uncertainty_std**2] * 3
        )
        vel_cov_init = np.diag(vel_cov_init_diag)

        initial_cov_ecef = np.block(
            [[pos_cov_init, np.zeros((3, 3))], [np.zeros((3, 3)), vel_cov_init]],
        )

        initial_state = State(
            state_vector=initial_state_ecef,
            timestamp=datetime.fromtimestamp(timestamp_ms / 1000.0),
        )
        # Set covariance separately if the State object supports it
        if hasattr(initial_state, "covar"):
            initial_state.covar = initial_cov_ecef

        # Extract ADS-B info if available
        adsb_info = original_detection_data.get("adsb_info", None)

        new_track = Track(
            initial_detection=original_detection_data,
            timestamp_ms=timestamp_ms,
            status=status,
            adsb_info=adsb_info,
        )

        # Add the initial state to the track
        new_track.append(initial_state)

        self.active_tracks[new_track.id] = new_track
        if self.config["verbose"]:
            track_type = (
                "ADS-B confirmed"
                if status == TrackStatus.CONFIRMED
                else "radar tentative"
            )
            print(
                f"Initiated new {track_type} track: {new_track.id} at ECEF {measurement_pos_ecef}",
            )

    def _manage_track_lifecycle(self):
        """@brief Updates track statuses (tentative to confirmed) and deletes old/unreliable tracks."""
        tracks_to_delete = []
        for track_id, track in self.active_tracks.items():
            if (
                track.status == TrackStatus.TENTATIVE
                and track.hits >= self.config["min_hits_to_confirm"]
            ):
                track.status = TrackStatus.CONFIRMED
                if self.config["verbose"]:
                    print(f"Track {track_id} confirmed.")

            if track.misses > self.config["max_misses_to_delete"]:
                tracks_to_delete.append(track_id)
                if self.config["verbose"]:
                    print(
                        f"Track {track_id} marked for deletion (misses: {track.misses}).",
                    )

        for track_id in tracks_to_delete:
            if track_id in self.active_tracks:
                del self.active_tracks[track_id]
                if self.config["verbose"]:
                    print(f"Deleted Track {track_id}.")

    def update_all_tracks(
        self,
        all_localised_detections_lla,
        current_timestamp_ms,
        adsb_detections_lla=None,
    ):
        """@brief Main entry point to update all tracks with new localised detections.
        @param all_localised_detections_lla (list): List of radar detection dicts, each with 'lla_position'.
        @param current_timestamp_ms (float): The current processing timestamp in milliseconds.
        @param adsb_detections_lla (list, optional): List of ADS-B detection dicts with 'lla_position' and 'adsb_info'.
        @return (dict): A dictionary of active Track objects {track_id: Track_object}.
        """
        # Delegate to Stone Soup tracker if available
        if self.stone_soup_tracker is not None:
            return self.stone_soup_tracker.update_all_tracks(
                all_localised_detections_lla,
                current_timestamp_ms,
                adsb_detections_lla
            )
        
        # Fallback to legacy implementation
        if self.last_timestamp_ms is None:
            self.last_timestamp_ms = current_timestamp_ms - (
                self.config["dt_default_s"] * 1000
            )  # Initialize for first dt

        dt_seconds = (current_timestamp_ms - self.last_timestamp_ms) / 1000.0
        if (
            dt_seconds <= 0
        ):  # Ensure dt is positive, can happen with out-of-order or identical timestamps
            if self.config["verbose"]:
                print(
                    f"Warning: dt_seconds is not positive ({dt_seconds}). Using default: {self.config['dt_default_s']}s",
                )
            dt_seconds = self.config["dt_default_s"]

        self.last_timestamp_ms = current_timestamp_ms

        # 1. Predict existing tracks to current time
        predicted_tracks_map = self._predict_tracks(dt_seconds)

        # 2. Handle ADS-B detections first (create confirmed tracks or update existing ones)
        if adsb_detections_lla:
            adsb_measurements = self._convert_localised_detections_to_measurements(
                adsb_detections_lla,
            )

            if self.config["verbose"]:
                print(f"Processing {len(adsb_measurements)} ADS-B measurements...")

            # Associate ADS-B detections with existing tracks (preferring ADS-B tracks)
            adsb_associations, unassoc_adsb_track_ids, unassoc_adsb_meas_indices = (
                self._data_association(predicted_tracks_map, adsb_measurements)
            )

            if self.config["verbose"]:
                print(
                    f"ADS-B associations: {len(adsb_associations)}, unassociated measurements: {len(unassoc_adsb_meas_indices)}",
                )

            # Update tracks associated with ADS-B detections
            for track_id, meas_idx in adsb_associations.items():
                if track_id not in self.active_tracks:
                    continue

                track = self.active_tracks[track_id]
                (
                    measurement_pos_ecef,
                    measurement_cov_ecef_pos,
                    original_detection_data,
                ) = adsb_measurements[meas_idx]

                if self.config["verbose"]:
                    adsb_hex = original_detection_data.get("adsb_info", {}).get(
                        "hex",
                        "unknown",
                    )
                    print(
                        f"Updating track {track_id} with ADS-B detection from aircraft {adsb_hex}",
                    )

                # Simplified update for ADS-B (high confidence)
                alpha = 0.8  # Higher weight for ADS-B measurements

                # Ensure consistent array shapes for state update
                track_pos = np.array(track.state_vector[:3]).flatten()
                meas_pos = np.array(measurement_pos_ecef).flatten()
                track_vel = np.array(track.state_vector[3:]).flatten()

                updated_state_pos = (1 - alpha) * track_pos + alpha * meas_pos
                updated_state = np.concatenate((updated_state_pos, track_vel))
                updated_covariance = track.covariance_matrix.copy()
                updated_covariance[:3, :3] = np.minimum(
                    track.covariance_matrix[:3, :3],
                    measurement_cov_ecef_pos,
                ) * (1 - alpha / 2)

                track.update(
                    detection=original_detection_data,
                    timestamp_ms=original_detection_data.get(
                        "timestamp_ms",
                        current_timestamp_ms,
                    ),
                    new_state=updated_state,
                    new_covariance=updated_covariance,
                )
                track.increment_age()

                # Update ADS-B info
                if "adsb_info" in original_detection_data:
                    track.adsb_info = original_detection_data["adsb_info"]

            # Create confirmed tracks for unassociated ADS-B detections
            for meas_idx in unassoc_adsb_meas_indices:
                (
                    measurement_pos_ecef,
                    measurement_cov_ecef_pos,
                    original_detection_data,
                ) = adsb_measurements[meas_idx]
                adsb_hex = original_detection_data.get("adsb_info", {}).get(
                    "hex",
                    "unknown",
                )
                if self.config["verbose"]:
                    print(
                        f"Creating new CONFIRMED track for unassociated ADS-B aircraft {adsb_hex}",
                    )

                self._initiate_new_track(
                    measurement_pos_ecef,
                    measurement_cov_ecef_pos,
                    original_detection_data,
                    original_detection_data.get("timestamp_ms", current_timestamp_ms),
                    status=TrackStatus.CONFIRMED,  # ADS-B tracks start as confirmed
                )

        # 3. Convert radar detections to measurements
        measurements = self._convert_localised_detections_to_measurements(
            all_localised_detections_lla,
        )

        # 4. Data Association for radar detections
        associations, unassociated_track_ids, unassociated_measurement_indices = (
            self._data_association(predicted_tracks_map, measurements)
        )

        # 5. Update Associated Tracks with radar detections
        for track_id, meas_idx in associations.items():
            if track_id not in self.active_tracks:
                continue  # Should not happen if predicted_tracks_map is from active_tracks

            track = self.active_tracks[track_id]
            measurement_pos_ecef, measurement_cov_ecef_pos, original_detection_data = (
                measurements[meas_idx]
            )

            # Simplified update - lower weight for radar measurements
            alpha = (
                0.6 if track.adsb_info is None else 0.4
            )  # Lower weight if track has ADS-B info

            # Ensure consistent array shapes for state update
            track_pos = np.array(track.state_vector[:3]).flatten()
            meas_pos = np.array(measurement_pos_ecef).flatten()
            track_vel = np.array(track.state_vector[3:]).flatten()

            updated_state_pos = (1 - alpha) * track_pos + alpha * meas_pos
            updated_state = np.concatenate((updated_state_pos, track_vel))
            # Simplified covariance update: assume measurement reduces uncertainty
            updated_covariance = track.covariance_matrix.copy()
            updated_covariance[:3, :3] = np.minimum(
                track.covariance_matrix[:3, :3],
                measurement_cov_ecef_pos,
            ) * (1 - alpha / 2)

            track.update(
                detection=original_detection_data,
                timestamp_ms=original_detection_data.get(
                    "timestamp_ms",
                    current_timestamp_ms,
                ),
                new_state=updated_state,
                new_covariance=updated_covariance,
            )

            track.increment_age()

        # 6. Handle Unassociated Tracks (increment misses)
        for track_id in unassociated_track_ids:
            if track_id in self.active_tracks:
                self.active_tracks[track_id].increment_misses()
                self.active_tracks[track_id].increment_age()

        # 7. Handle Unassociated Radar Measurements (initiate new tentative tracks)
        for meas_idx in unassociated_measurement_indices:
            measurement_pos_ecef, measurement_cov_ecef_pos, original_detection_data = (
                measurements[meas_idx]
            )
            self._initiate_new_track(
                measurement_pos_ecef,
                measurement_cov_ecef_pos,
                original_detection_data,
                original_detection_data.get("timestamp_ms", current_timestamp_ms),
                status=TrackStatus.TENTATIVE,  # Radar tracks start as tentative
            )

        # 8. Manage Track Lifecycle (confirm tentative, delete old)
        self._manage_track_lifecycle()

        # 9. Log comprehensive track states
        if self.config["verbose"]:
            self._log_all_track_states(current_timestamp_ms)

        return self.active_tracks.copy()  # Return a copy

    def _log_all_track_states(self, timestamp_ms):
        """Log detailed state information for all active tracks."""
        if not self.active_tracks:
            print(f"[TRACKER {timestamp_ms}] No active tracks")
            return

        print(
            f"[TRACKER {timestamp_ms}] === TRACK SUMMARY ({len(self.active_tracks)} active) ===",
        )

        adsb_tracks = []
        radar_tracks = []

        for track_id, track in self.active_tracks.items():
            track_info = {
                "id": track_id,
                "status": track.status.name,
                "hits": track.hits,
                "misses": track.misses,
                "age": track.age_scans,
                "pos": track.state_vector[:3]
                if track.state_vector is not None
                else None,
                "vel": track.state_vector[3:6]
                if track.state_vector is not None and len(track.state_vector) >= 6
                else None,
                "adsb": track.adsb_info,
            }

            if track.adsb_info:
                adsb_tracks.append(track_info)
            else:
                radar_tracks.append(track_info)

        # Log ADS-B tracks
        if adsb_tracks:
            print(f"[TRACKER {timestamp_ms}] ADS-B TRACKS ({len(adsb_tracks)}):")
            for track in adsb_tracks:
                flight_info = (
                    track["adsb"]["flight"]
                    if track["adsb"] and track["adsb"].get("flight")
                    else track["adsb"]["hex"]
                    if track["adsb"]
                    else "N/A"
                )
                pos_str = (
                    f"[{track['pos'][0]:.1f}, {track['pos'][1]:.1f}, {track['pos'][2]:.1f}]"
                    if track["pos"] is not None
                    else "N/A"
                )
                vel_str = (
                    f"[{track['vel'][0]:.1f}, {track['vel'][1]:.1f}, {track['vel'][2]:.1f}]"
                    if track["vel"] is not None
                    else "N/A"
                )
                print(
                    f"  ✈️  {track['id']} ({flight_info}) - {track['status']} - Pos: {pos_str} - Vel: {vel_str} - H:{track['hits']} M:{track['misses']} A:{track['age']}",
                )

        # Log radar tracks
        if radar_tracks:
            print(f"[TRACKER {timestamp_ms}] RADAR TRACKS ({len(radar_tracks)}):")
            for track in radar_tracks:
                pos_str = (
                    f"[{track['pos'][0]:.1f}, {track['pos'][1]:.1f}, {track['pos'][2]:.1f}]"
                    if track["pos"] is not None
                    else "N/A"
                )
                vel_str = (
                    f"[{track['vel'][0]:.1f}, {track['vel'][1]:.1f}, {track['vel'][2]:.1f}]"
                    if track["vel"] is not None
                    else "N/A"
                )
                status_icon = (
                    "🎯"
                    if track["status"] == "CONFIRMED"
                    else "⚡"
                    if track["status"] == "COASTING"
                    else "❓"
                )
                print(
                    f"  {status_icon}  {track['id']} - {track['status']} - Pos: {pos_str} - Vel: {vel_str} - H:{track['hits']} M:{track['misses']} A:{track['age']}",
                )

        print(f"[TRACKER {timestamp_ms}] === END TRACK SUMMARY ===")
