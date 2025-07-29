"""@file Geometry.py
@author 30hours
"""

import math


class Geometry:
    """@class Geometry
    @brief A class to store geometric functions for passive radar applications.
    @details Uses ENU coordinate system for all internal calculations. 
    Input and output should be LLA. WGS-84 ellipsoid assumed.
    """

    def __init__(self):
        """@brief Constructor for the Geometry class."""

    def lla2enu(lat, lon, alt, ref_lat, ref_lon, ref_alt):
        """@brief Converts geodetic coordinates to East-North-Up (ENU) coordinates.
        @param lat (float): Target geodetic latitude in degrees.
        @param lon (float): Target geodetic longitude in degrees.
        @param alt (float): Target altitude above ellipsoid in meters.
        @param ref_lat (float): Reference geodetic latitude in degrees.
        @param ref_lon (float): Reference geodetic longitude in degrees.
        @param ref_alt (float): Reference altitude above ellipsoid in meters.
        @return east (float): East coordinate in meters.
        @return north (float): North coordinate in meters.
        @return up (float): Up coordinate in meters.
        """
        # Convert to radians
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        ref_lat_rad = math.radians(ref_lat)
        ref_lon_rad = math.radians(ref_lon)
        
        # Difference in coordinates
        dlat = lat_rad - ref_lat_rad
        dlon = lon_rad - ref_lon_rad
        dalt = alt - ref_alt
        
        # Earth radius approximation (WGS84)
        a = 6378137.0  # semi-major axis in meters
        
        # Convert to ENU
        east = a * math.cos(ref_lat_rad) * dlon
        north = a * dlat
        up = dalt
        
        return east, north, up

    def enu2lla(east, north, up, ref_lat, ref_lon, ref_alt):
        """@brief Converts East-North-Up (ENU) coordinates to geodetic coordinates.
        @param east (float): East coordinate in meters.
        @param north (float): North coordinate in meters.
        @param up (float): Up coordinate in meters.
        @param ref_lat (float): Reference geodetic latitude in degrees.
        @param ref_lon (float): Reference geodetic longitude in degrees.
        @param ref_alt (float): Reference altitude above ellipsoid in meters.
        @return lat (float): Target geodetic latitude in degrees.
        @return lon (float): Target geodetic longitude in degrees.
        @return alt (float): Target altitude above ellipsoid in meters.
        """
        # Convert reference to radians
        ref_lat_rad = math.radians(ref_lat)
        ref_lon_rad = math.radians(ref_lon)
        
        # Earth radius approximation (WGS84)
        a = 6378137.0  # semi-major axis in meters
        
        # Convert from ENU to LLA differences
        dlat = north / a
        dlon = east / (a * math.cos(ref_lat_rad))
        dalt = up
        
        # Add to reference position
        lat = math.degrees(ref_lat_rad + dlat)
        lon = math.degrees(ref_lon_rad + dlon)
        alt = ref_alt + dalt
        
        # Normalize longitude to [-180, 180] range
        while lon > 180:
            lon -= 360
        while lon < -180:
            lon += 360
            
        return lat, lon, alt

    def distance_enu(point1, point2):
        """@brief Computes the Euclidean distance between two points in ENU coordinates.
        @param point1 (tuple): Coordinates of the first point (east, north, up) in meters.
        @param point2 (tuple): Coordinates of the second point (east, north, up) in meters.
        @return distance (float): Euclidean distance between the two points in meters.
        """
        return math.sqrt(
            (point2[0] - point1[0]) ** 2
            + (point2[1] - point1[1]) ** 2
            + (point2[2] - point1[2]) ** 2,
        )

    def average_points(points):
        """@brief Computes the average point from a list of points.
        @param points (list): List of points, where each point is a tuple of coordinates (x, y, z) in meters.
        @return average_point (list): Coordinates of the average point (x_avg, y_avg, z_avg) in meters.
        """
        return [sum(coord) / len(coord) for coord in zip(*points)]
