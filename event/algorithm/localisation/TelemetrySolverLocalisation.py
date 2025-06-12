import sys
import os
sys.path.append('/app/TelemetrySolver')

from detection_triple import DetectionTriple, Detection
from initial_guess_3det import get_initial_guess
from lm_solver_3det import solve_position_velocity_3d

class TelemetrySolverLocalisation:
    """TelemetrySolver integration into 3lips localization pipeline."""
    
    def __init__(self):
        pass
        
    def process(self, assoc_detections, radar_data):
        """Process detections using TelemetrySolver.
        
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
                    # Convert to Detection objects
                    detections = []
                    for radar in assoc_detections[target][:3]:
                        config = radar_data[radar["radar"]]["config"]
                        detection_data = {
                            "sensor_lat": config["location"]["rx"]["latitude"],
                            "sensor_lon": config["location"]["rx"]["longitude"],
                            "ioo_lat": config["location"]["tx"]["latitude"],
                            "ioo_lon": config["location"]["tx"]["longitude"],
                            "freq_mhz": config["frequency"] / 1e6,
                            "timestamp": radar["timestamp"],
                            "bistatic_range_km": radar["delay"],
                            "doppler_hz": radar["doppler"]
                        }
                        detections.append(Detection(**detection_data))
                    
                    # Create DetectionTriple
                    triple = DetectionTriple(detections[0], detections[1], detections[2])
                    
                    # Generate initial guess
                    initial_guess = get_initial_guess(triple)
                    
                    # Solve using LM optimizer
                    result = solve_position_velocity_3d(triple, initial_guess)
                    
                    if result and "error" not in result:
                        output[target] = {
                            "points": [[
                                result["lat"],
                                result["lon"],
                                result["alt"]
                            ]]
                        }
                        print(f"TelemetrySolver result for {target}: {result}")
                    else:
                        print(f"TelemetrySolver failed for {target}: {result}")
                        
                except Exception as e:
                    print(f"TelemetrySolver error for {target}: {e}")
                    
        return output