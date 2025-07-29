"""@file Geometry.py
@author 30hours
@brief Import geometry functions directly from RETINAsolver
"""

import os
import sys

# Import RETINAsolver geometry functions directly
retina_solver_path = os.environ.get("RETINA_SOLVER_PATH", "/app/RETINAsolver")
if retina_solver_path not in sys.path:
    sys.path.append(retina_solver_path)

try:
    # Import the entire Geometry class from RETINAsolver
    from Geometry import Geometry
except ImportError as e:
    # Fallback for testing environments where RETINAsolver isn't available
    import numpy as np
    
    class MockGeometry:
        """Fallback Geometry implementation for testing when RETINAsolver is not available."""
        
        @staticmethod
        def lla2enu(lat, lon, alt, ref_lat, ref_lon, ref_alt):
            """Mock LLA to ENU conversion for testing."""
            # Simple mock conversion - in real tests, specific values would be set
            # This is just to prevent import errors during testing
            dlat = lat - ref_lat
            dlon = lon - ref_lon
            dalt = alt - ref_alt
            
            # Very rough approximation for testing purposes
            east = dlon * 111320.0 * np.cos(np.radians(ref_lat))
            north = dlat * 110540.0
            up = dalt
            
            return east, north, up
        
        @staticmethod
        def enu2lla(east, north, up, ref_lat, ref_lon, ref_alt):
            """Mock ENU to LLA conversion for testing."""
            # Very rough approximation for testing purposes
            dlat = north / 110540.0
            dlon = east / (111320.0 * np.cos(np.radians(ref_lat)))
            dalt = up
            
            lat = ref_lat + dlat
            lon = ref_lon + dlon
            alt = ref_alt + dalt
            
            return lat, lon, alt
        
        @staticmethod
        def lla2ecef(lat, lon, alt):
            """Mock LLA to ECEF conversion for testing."""
            # Simplified mock - returns (x, y, z) coordinates
            x = (6378137.0 + alt) * np.cos(np.radians(lat)) * np.cos(np.radians(lon))
            y = (6378137.0 + alt) * np.cos(np.radians(lat)) * np.sin(np.radians(lon))
            z = ((6378137.0 * 0.996647) + alt) * np.sin(np.radians(lat))
            return x, y, z
        
        @staticmethod
        def ecef2lla(x, y, z):
            """Mock ECEF to LLA conversion for testing."""
            # Simplified mock conversion
            p = np.sqrt(x**2 + y**2)
            lat = np.arctan2(z, p)
            lon = np.arctan2(y, x)
            alt = p / np.cos(lat) - 6378137.0
            return np.degrees(lat), np.degrees(lon), alt
    
    # Use mock geometry in testing environments
    print(f"Warning: Using mock Geometry implementation. RETINAsolver not available at {retina_solver_path}")
    Geometry = MockGeometry

# Make it available for 3lips components
__all__ = ["Geometry"]
