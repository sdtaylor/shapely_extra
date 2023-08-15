import numpy as np
from shapely_extra.angles import pointFromAngleAndDistance
from shapely.geometry import Point, Polygon

from math import (
    radians, degrees, sin, cos, sqrt, pi, isclose)

import numbers

def hexagon(center=(0,0), sidelength=1, area=None):
    """
    Create a hexagon centered on origin(x,y), with either sidelength 
    or area specified. 
    
    From https://www.redblobgames.com/grids/hexagons/

    Parameters
    ----------
    center : tuple, optional
        (x,y) coordinates of the center of the hexagon. The default is (0,0).
    sidelength : numeric
        Length of each edge of the hexagon. Ignored if area is specified.
    area : numeric
        The desired area of the hexagon. The required sidelength will
        be calculated.

    Returns
    -------
    Polygon.

    """
    if area is not None:
        h = sqrt( (area*2) /  (3*sqrt(3)) )
    else:
        h = sidelength

    center_x, center_y = center

    hex_points = []
    for i in range(6):
        angle_deg = 60 * i
        angle_rad = pi / 180 * angle_deg
        hex_points.append(
            Point(center_x + h * cos(angle_rad),
                  center_y + h * sin(angle_rad)))
        
    return Polygon(hex_points)

# def triangle(center = (0,0), angles = (60,60,60), area=1, lengths=None):
#     """
    
#     If lengths is specified then angles is ignored.

#     Parameters
#     ----------
#     center : TYPE, optional
#         DESCRIPTION. The default is (0,0).
#     angles : TYPE, optional
#         DESCRIPTION. The default is (60,60,60).
#     lengths : TYPE, optional
#         DESCRIPTION. The default is None.
#     area : TYPE, optional
#         DESCRIPTION. The default is None.

#     Returns
#     -------
#     None.

#     """
    
#     pass

def square(center = (0,0), sidelength=1, area=None):
    """
    Create a square with a specified side length or area.
    
    If area is specified then sidelength is ignored. 

    Parameters
    ----------
    center : tuple, optional
        (x,y) coordinates of the center of the hexagon. The default is (0,0).
    sidelength : numeric, optional
        The length of 1 side of the square. Ignored if area is specified.
    area : numeric, optional
        Desired area of the square. The default is None.

    Returns
    -------
    Polygon.

    """
    if area is not None:
        sidelength = sqrt(area)
    
    half_length = sidelength/2
    ll = Point(center[0] - half_length, center[1] - half_length)
    lr = Point(center[0] + half_length, center[1] - half_length)
    ur = Point(center[0] + half_length, center[1] + half_length)
    ul = Point(center[0] - half_length, center[1] + half_length)
    
    return Polygon([ll, lr, ur, ul])

def circle(center=(0,0), radius=1, circumference=None, area=None, tolerance=0.1):
    """
    Create a circle centered on origin(x,y), with either radius 
    or area specified. 
    
    A wrapper around Point(x,y).buffer(distance=radius), but this also 
    densifies the polygon so that the circle area approximates the true area, 
    up to the tolerance specified.
    
    For example, a circle with radius 1 has area of pi, but:
        Point(0,0).buffer(1).area = 3.136548...
        
    This can be resolved by creating a denser buffer:
        Point(0,0).buffer(1, quad_segs=300).area = 3.1415782

    Here the circle will be densified by increasing the quad_segs argument
    until the area is equal to the true area of  r*pi**2, up until the 
    specified tolerance.    

    Argument priority is as follows:
        1. area. If area is specified then radius and circumference are ignored.
        2. circumference. If specified then radius is ignored.
        3. radius. 

    Parameters
    ----------
    center : tuple, optional
        (x,y) coordinates of the center of the hexagon. The default is (0,0).
    radius : numeric, optional
        The desired radius of the circle. Ignored if area is specified.
    circumference : numeric, optional
        The desirec circumference of the circule.
    area : numeric, optional
        The desired area of the circle. 
    tolerance : numeric, optional
        How close to the true circle area. This is the absolute tolerance. So
        for example with tolerance=10, the  derived area of the returned circle
        will be ± 10 units to the true area.  
        The default is 0.1 units.

    Returns
    -------
    Polygon.

    """
    if area is not None:
        if not isinstance(area, numbers.Number):
            raise TypeError('area must be a numeric type')
        
        r = sqrt(area / pi)
        
    elif circumference is not None:
        if not isinstance(circumference, numbers.Number):
            raise TypeError('circumference must be a numeric type')
            
        r = circumference / (2*pi)
        
    elif radius is not None:
        if not isinstance(radius, numbers.Number):
            raise TypeError('radius must be a numeric type')
        
        r = radius
    
    else:
        raise ValueError('either radius, circumference, or area must be specified')
    
    if tolerance<=0:
        msg = (
            'tolerance should be > 0. If you want a small tolerance try a small number',
            'like 1e-6'
            )
        raise ValueError(msg)
    
    true_area = pi * r**2
    
    #TODO: a better gradient function could speed this up.
    segment_step_size = 10
    for i in range(1000):
        segements_to_try = segment_step_size * i
        derived_area = Point(center).buffer(distance=r, quad_segs=segements_to_try).area
        if isclose(derived_area, true_area, abs_tol=tolerance):
            break
    
    return Point(center).buffer(distance=r, quad_segs=segements_to_try)
    
    

    