"""@file Ellipsoid.py
@author 30hours
"""

import math

from algorithm.geometry.Geometry import Geometry


class Ellipsoid:
    """@class Ellipsoid
    @brief A class to store ellipsoid parameters for bistatic radar.
    @details Stores foci, midpoint, pitch, yaw and distance.
    """

    def __init__(self, f1_lla, f2_lla, name):
        """@brief Constructor for the Ellipsoid class.
        @param f1_lla (list): [lat, lon, alt] of foci 1 in degrees and meters.
        @param f2_lla (list): [lat, lon, alt] of foci 2 in degrees and meters.
        @param name (str): Name to associate with shape.
        """
        self.f1_lla = f1_lla
        self.f2_lla = f2_lla
        self.name = name

        # dependent members
        # Calculate midpoint in LLA
        self.midpoint_lla = [
            (f1_lla[0] + f2_lla[0]) / 2,
            (f1_lla[1] + f2_lla[1]) / 2,
            (f1_lla[2] + f2_lla[2]) / 2
        ]
        
        # Convert f1 to ENU relative to midpoint to calculate angles
        e1, n1, u1 = Geometry.lla2enu(
            f1_lla[0], f1_lla[1], f1_lla[2],
            self.midpoint_lla[0], self.midpoint_lla[1], self.midpoint_lla[2]
        )
        
        # Calculate yaw and pitch from ENU vector
        self.yaw = -math.atan2(n1, e1)
        self.pitch = math.atan2(
            u1,
            math.sqrt(e1 ** 2 + n1 ** 2),
        )
        
        # Calculate distance between foci
        self.distance = Geometry.distance_lla(f1_lla, f2_lla)
