import numpy as np
from shapely.geometry import Point, Polygon

from math import (
    radians, degrees, sin, cos, sqrt, pi, isclose)

import numbers

from typing import Union

def hexagon(center: tuple[float,float] = (0,0), 
            sidelength:float = 1, 
            area: Union[float, None] = None) -> Polygon:
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

def square(center: tuple[float,float] = (0,0), 
           sidelength:float = 1, 
           area: Union[float,None] = None) -> Polygon:
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

def circle(center: tuple[float,float] = (0,0), 
           radius:float = 1, 
           circumference: Union[float,None] = None, 
           area: Union[float,None] = None, 
           rel_tolerance:float = 0.01, 
           abs_tolerance: Union[float,None] = None):
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
    rel_tolerance : numeric, optional
        How close to the true circle area. This is the relative tolerance. For
        example with rel_tolerance=0.01 (the default) the derived area of the 
        returned circle will be ± 1% of the true area.
        Ignored if abs_tolerance is specified
    abs_tolerance : numeric, optional
        How close to the true circle area. This is the absolute tolerance. So
        for example with abs_tolerance=10, the  derived area of the returned circle
        will be ± 10 units to the true area.  
        The default is None.

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
    
    true_area = pi * r**2
    
    if abs_tolerance is not None:
        if abs_tolerance<=0:
            msg = (
            'abs_tolerance should be > 0. If you want a small tolerance try a small number',
            'like 1e-6'
            )
            raise ValueError(msg)
        tol = abs_tolerance
    else:
        if rel_tolerance<=0:
            raise ValueError('rel_tolerance should be > 0.')
        tol = rel_tolerance * true_area
    
    #TODO: a better gradient function could speed this up.
    # potential approximate solution: https://math.stackexchange.com/questions/4132060/compute-number-of-regular-polgy-sides-to-approximate-circle-to-defined-precision
    for n_segs_per_qtr_circle in range(1,10000):
        n_segs_per_circle = n_segs_per_qtr_circle * 4
        # A circle polygon is a ring of evenly distributed points, where the
        # line between each point makes a segment. A shapely
        # buffer distributes the points evenly between the 4 quarters. 
        # Each segment is a triangle with 2 adjacent sides equal to the radius.
        # Find the triangle area to find the area made by the circle polygon
        interior_angle = 360/n_segs_per_circle
        triangle_area = sin(radians(interior_angle)) * (r**2) * 0.5
        derived_area = triangle_area * n_segs_per_circle

        if abs(true_area - derived_area) <= tol:
            break
    
    return Point(center).buffer(distance=r, quad_segs=n_segs_per_qtr_circle)
