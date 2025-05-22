import numpy as np
import uuid
from enum import Enum, auto

# Define track status as an Enum
class TrackStatus(Enum):
    TENTATIVE = auto()
    CONFIRMED = auto()
    COASTING = auto()
    DELETED = auto()

class Track:
    """
    @class Track
    @brief A class to store and manage information for a single track.
    """

    def __init__(self, initial_detection, timestamp_ms, initial_state, initial_covariance, track_id=None):
        """
        @brief Constructor for the Track class.
        @param initial_detection: The first detection object or data that initiated this track.
        @param timestamp_ms (float): Timestamp of track initiation in milliseconds.
        @param initial_state (np.ndarray): Initial state vector (e.g., [x, y, z, vx, vy, vz]).
        @param initial_covariance (np.ndarray): Initial covariance matrix for the state vector.
        @param track_id (str, optional): A unique ID for the track. If None, a UUID will be generated.
        """
        self.track_id = track_id if track_id is not None else str(uuid.uuid4())
        
        self.state_vector = np.asarray(initial_state)
        self.covariance_matrix = np.asarray(initial_covariance)
        
        self.timestamp_creation_ms = timestamp_ms
        self.timestamp_update_ms = timestamp_ms
        
        self.status = TrackStatus.TENTATIVE
        
        # History can store a list of (timestamp, state_vector, covariance_matrix) tuples
        self.history = [(timestamp_ms, self.state_vector.copy(), self.covariance_matrix.copy())]
        
        # Detections that formed/updated this track. Could store raw detection objects or their IDs.
        self.associated_detections_history = [initial_detection] 
        
        self.hits = 1  # Number of detections successfully associated with this track
        self.misses = 0  # Number of consecutive times this track was not updated with a detection
        self.age_scans = 1 # Number of scans this track has existed for (can be updated by tracker)

        # Placeholder for a filter object (e.g., KalmanFilter instance)
        # This would be initialized and used by the Tracker class
        self.filter = None 

        # Optional: Store other metrics
        self.adsb_info = None # To store associated ADS-B data if available
        self.last_chi_squared = None # Store chi-squared from last update for gating/quality

    def predict(self, dt_seconds):
        """
        @brief Predicts the next state of the track.
               This is a placeholder. Actual prediction logic using a motion model
               (e.g., Constant Velocity) and the filter's predict step would be more complex
               and likely handled by a dedicated filter object or the Tracker class.
        @param dt_seconds (float): Time delta in seconds since the last update.
        @return: Predicted state_vector and covariance_matrix.
        """
        # Example: Simple constant velocity prediction (assumes state is [x,y,z,vx,vy,vz,...])
        # This should be replaced by a proper filter.predict() call
        if self.filter:
            self.filter.predict(dt=dt_seconds)
            self.state_vector = self.filter.x
            self.covariance_matrix = self.filter.P
        else:
            # Very basic placeholder if no filter is attached yet
            # For a CV model: x_new = x_old + vx * dt
            if len(self.state_vector) >= 6: # Assuming at least x,y,z,vx,vy,vz
                F = np.array([
                    [1, 0, 0, dt_seconds, 0,          0],
                    [0, 1, 0, 0,          dt_seconds, 0],
                    [0, 0, 1, 0,          0,          dt_seconds],
                    [0, 0, 0, 1,          0,          0],
                    [0, 0, 0, 0,          1,          0],
                    [0, 0, 0, 0,          0,          1]
                ])
                # This is a simplification; process noise should be added to covariance.
                if self.state_vector.shape[0] == F.shape[1]: # Ensure dimensions match for state
                     self.state_vector = F @ self.state_vector
                # Covariance prediction: P_new = F @ P_old @ F.T + Q (Q is process noise)
                # self.covariance_matrix = F @ self.covariance_matrix @ F.T + Q_matrix 
                # (Q_matrix needs to be defined)

        return self.state_vector, self.covariance_matrix

    def update(self, detection, timestamp_ms, new_state, new_covariance):
        """
        @brief Updates the track with a new associated detection and filter output.
        @param detection: The detection object or data associated with this track.
        @param timestamp_ms (float): Timestamp of this update in milliseconds.
        @param new_state (np.ndarray): The updated state vector from the filter.
        @param new_covariance (np.ndarray): The updated covariance matrix from the filter.
        """
        self.state_vector = np.asarray(new_state)
        self.covariance_matrix = np.asarray(new_covariance)
        self.timestamp_update_ms = timestamp_ms
        
        self.history.append((timestamp_ms, self.state_vector.copy(), self.covariance_matrix.copy()))
        self.associated_detections_history.append(detection)
        
        self.hits += 1
        self.misses = 0 # Reset misses on successful update
        
        if self.status == TrackStatus.TENTATIVE and self.hits > 3: # Example confirmation logic
            self.status = TrackStatus.CONFIRMED

    def increment_misses(self):
        """
        @brief Increments the miss counter.
        """
        self.misses += 1
        if self.status == TrackStatus.CONFIRMED and self.misses > 3: # Example coasting logic
            self.status = TrackStatus.COASTING
        # Deletion logic based on misses would typically be in the Tracker class

    def increment_age(self):
        """
        @brief Increments the age of the track (in terms of scans/updates).
        """
        self.age_scans +=1

    def get_position_lla(self):
        """
        @brief Returns the track's current position in LLA (Latitude, Longitude, Altitude).
               This assumes the state vector stores position in a way that can be converted
               or is already LLA. This might require using Geometry.py functions.
               Placeholder: Assumes first three elements are LLA directly for simplicity.
        @return (tuple | None): (lat, lon, alt) or None if not applicable.
        """
        # This is a placeholder. You'll need to decide how ECEF/LLA/ENU are handled.
        # If state_vector is ECEF:
        # from algorithm.geometry.Geometry import Geometry # Potentially circular, manage imports
        # return Geometry.ecef2lla(self.state_vector[0], self.state_vector[1], self.state_vector[2])
        # If state_vector directly contains LLA:
        if len(self.state_vector) >= 3:
            return (self.state_vector[0], self.state_vector[1], self.state_vector[2])
        return None

    def to_dict(self):
        """
        @brief Returns a dictionary representation of the track, suitable for JSON serialization.
        """
        history_serializable = []
        for ts, state, cov in self.history:
            history_serializable.append({
                "timestamp_ms": ts,
                "state_vector": state.tolist(),
                "covariance_matrix": cov.tolist()
            })
            
        return {
            "track_id": self.track_id,
            "status": self.status.name,  # Use enum name for serialization
            "timestamp_creation_ms": self.timestamp_creation_ms,
            "timestamp_update_ms": self.timestamp_update_ms,
            "current_state_vector": self.state_vector.tolist(),
            "current_covariance_matrix": self.covariance_matrix.tolist(),
            "hits": self.hits,
            "misses": self.misses,
            "age_scans": self.age_scans,
            "adsb_info": self.adsb_info, # if populated
            "history_len": len(self.history) # For brevity, not sending full history by default
            # "history": history_serializable, # Optionally include full history
        }

    def __repr__(self):
        return (f"Track(ID: {self.track_id}, Status: {self.status.name}, "
                f"Pos: {self.state_vector[:3]}, LastUpdate: {self.timestamp_update_ms})")

