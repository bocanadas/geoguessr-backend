"""
Distance calculation and scoring functions for GeoGuessr game.

Uses the Haversine formula (via geopy) to calculate great-circle distance
between two points on Earth's surface.
"""

import math
from geopy.distance import distance


def calculate_distance(lat1, lng1, lat2, lng2):
    """
    Calculate distance in kilometers between two coordinates.

    Args:
        lat1 (float): Latitude of first point
        lng1 (float): Longitude of first point
        lat2 (float): Latitude of second point
        lng2 (float): Longitude of second point

    Returns:
        float: Distance in kilometers
    """
    point1 = (lat1, lng1)
    point2 = (lat2, lng2)
    return distance(point1, point2).km


def calculate_score(distance_km):
    """
    Convert distance to score (0-5000) using exponential decay.

    The scoring mimics real GeoGuessr:
    - 0 km = 5000 points (perfect guess)
    - ~10 km = ~4750 points
    - ~100 km = ~3800 points
    - ~1000 km = ~1500 points
    - 20000+ km = 0 points

    Formula: score = 5000 * e^(-distance / 2000)

    Args:
        distance_km (float): Distance in kilometers

    Returns:
        int: Score from 0 to 5000
    """
    if distance_km > 20000:
        return 0

    # Exponential decay: heavily rewards accuracy
    score = 5000 * math.exp(-distance_km / 2000)
    return round(score)
