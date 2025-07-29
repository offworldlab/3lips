import os
import sys

retina_solver_path = os.environ.get("RETINA_SOLVER_PATH", "/app/RETINAsolver")
if retina_solver_path not in sys.path:
    sys.path.append(retina_solver_path)

from detection_triple import Detection, DetectionTriple  # noqa: E402
from initial_guess_3det import get_initial_guess  # noqa: E402
from lm_solver_3det import solve_position_velocity_3d  # noqa: E402


class RETINASolverLocalisation:
    """RETINASolver integration into 3lips localization pipeline."""

    def __init__(self):
        pass

    def process(self, assoc_detections, radar_data):
        """Process detections using RETINASolver.

        Args:
            assoc_detections (dict): Associated detections by target ID
            radar_data (dict): Radar configuration data

        Returns:
            dict: Localized positions in 3lips format
        """
        output = {}

        for target in assoc_detections:
            if len(assoc_detections[target]) >= 3:
                try:
                    detections = []
                    for radar in assoc_detections[target][:3]:
                        detections.append(self._create_detection(radar, radar_data))

                    triple = DetectionTriple(
                        detections[0], detections[1], detections[2]
                    )
                    initial_guess = get_initial_guess(triple)
                    result = solve_position_velocity_3d(triple, initial_guess)

                    if result and "error" not in result:
                        output[target] = {
                            "points": [[result["lat"], result["lon"], result["alt"]]]
                        }
                except Exception:  # nosec B110
                    pass

        return output

    def _create_detection(self, radar, radar_data):
        config = radar_data[radar["radar"]]["config"]
        return Detection(
            sensor_lat=config["location"]["rx"]["latitude"],
            sensor_lon=config["location"]["rx"]["longitude"],
            ioo_lat=config["location"]["tx"]["latitude"],
            ioo_lon=config["location"]["tx"]["longitude"],
            freq_mhz=config["frequency"] / 1e6,
            timestamp=radar["timestamp"],
            bistatic_range_km=radar["delay"],
            doppler_hz=radar["doppler"],
        )
