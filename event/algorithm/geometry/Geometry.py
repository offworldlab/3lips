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
    # Fallback error handling for development/testing environments
    raise ImportError(
        f"Could not import Geometry from RETINAsolver at {retina_solver_path}. "
        f"Please ensure RETINA_SOLVER_PATH environment variable is set correctly "
        f"and RETINAsolver is available. Original error: {e}"
    )

# Make it available for 3lips components
__all__ = ['Geometry']