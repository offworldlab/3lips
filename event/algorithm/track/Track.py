from stonesoup.types.track import Track as StoneSoupTrack
from enum import Enum, auto

# Define track status as an Enum
class TrackStatus(Enum):
    TENTATIVE = auto()
    CONFIRMED = auto()
    COASTING = auto()
    DELETED = auto()

class Track(StoneSoupTrack):
    """
    Extension of Stone-Soup's Track to add custom fields and logic for 3lips.
    """
    def __init__(self, *args, status=TrackStatus.TENTATIVE, filter_obj=None, adsb_info=None, last_chi_squared=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Custom fields
        self.status = status
        self.filter = filter_obj  # Placeholder for a filter object (e.g., KalmanFilter instance)
        self.adsb_info = adsb_info  # To store associated ADS-B data if available
        self.last_chi_squared = last_chi_squared  # Store chi-squared from last update for gating/quality
        self.hits = 1  # Number of detections successfully associated with this track
        self.misses = 0  # Number of consecutive times this track was not updated with a detection
        self.age_scans = 1 # Number of scans this track has existed for
        self.associated_detections_history = []  # Detections that formed/updated this track

    def update_custom(self, detection, status=None, adsb_info=None, last_chi_squared=None):
        """
        Update custom fields after a new detection is associated.
        """
        self.associated_detections_history.append(detection)
        self.hits += 1
        self.misses = 0
        if status is not None:
            self.status = status
        if adsb_info is not None:
            self.adsb_info = adsb_info
        if last_chi_squared is not None:
            self.last_chi_squared = last_chi_squared
        if self.status == TrackStatus.TENTATIVE and self.hits > 3:
            self.status = TrackStatus.CONFIRMED

    def increment_misses(self):
        """
        Increments the miss counter and updates status if needed.
        """
        self.misses += 1
        if self.status == TrackStatus.CONFIRMED and self.misses > 3:
            self.status = TrackStatus.COASTING

    def increment_age(self):
        """
        Increments the age of the track (in terms of scans/updates).
        """
        self.age_scans += 1

    def get_position_lla(self):
        """
        Returns the track's current position in LLA (Latitude, Longitude, Altitude).
        Assumes the state vector stores position in a way that can be converted or is already LLA.
        """
        if self.states and len(self.states[-1].state_vector) >= 3:
            sv = self.states[-1].state_vector
            return (sv[0], sv[1], sv[2])
        return None

    def to_dict(self):
        """
        Returns a dictionary representation of the track, suitable for JSON serialization.
        """
        return {
            "track_id": self.id,
            "status": self.status.name if hasattr(self.status, 'name') else str(self.status),
            "current_state_vector": self.states[-1].state_vector.tolist() if self.states else None,
            "hits": self.hits,
            "misses": self.misses,
            "age_scans": self.age_scans,
            "adsb_info": self.adsb_info,
            "history_len": len(self.states),
        }

    def __repr__(self):
        pos = self.states[-1].state_vector[:3] if self.states else None
        return (f"Track(ID: {self.id}, Status: {self.status}, Pos: {pos}, Hits: {self.hits}, Misses: {self.misses})")

