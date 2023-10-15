from math import (
    radians, degrees, sin, cos, atan2, pi)

from shapely.geometry import Point, LineString

# Thse are a few generalized angle methods designed to
# work with shapely Point and Linestring

# because pi is infinate there will always be some rounding errors.
# Setting some precision ensures that, for example, sin(pi) = 0
DECIMAL_PRECISION = 8

def radians_to_degrees(radians):
    """
    Converts from radians to degrees.

    Parameters
    ----------
    radians : float
        An angle in radians.

    Returns
    -------
    float
        An angle in degrees

    """
    return degrees(radians)

def degrees_to_radians(angleDegrees):
    """
    Converts from degrees to radians.

    Parameters
    ----------
    angleDegrees : float
        An angle in degrees.

    Returns
    -------
    float
        An angle in radians.

    """
    return radians(angleDegrees)

def angle_between_points(p0, p1):
    """
    The angle of the vector from Points p0 to p1, relative to the positive x-axis.

    Parameters
    ----------
    p0 : Point or tuple
        A shapely Point object or (x,y) tuple
    p1 : Point or tuple
        A shapely Point object or (x,y) tuple

    Returns
    -------
    float
        The angle, in radians, is normalized to be in the range [ -Pi, Pi ].

    """
    if isinstance(p0, Point) and isinstance(p1, Point):
        dx = p1.x - p0.x
        dy = p1.y - p0.y
    elif isinstance(p0, tuple) and isinstance(p1, tuple):
        dx = p1[0] - p0[0]
        dy = p1[1] - p0[1]
    else:
        raise TypeError('p0 and p1 must be shapely.geometry.Point or (x,y) tuples')

    return atan2(dy,dx)

def angle_diff(angle1, angle2):
    """
    The unoriented smallest difference between two angles.

    Parameters
    ----------
    angle1 : float
        Angle in radians in the range (-Pi,Pi)
    angle2 : float
        Angle in radians in the range (-Pi,Pi)

    Returns
    -------
    float
        Angle in radians in the range (0,Pi)

    """
    if angle1 < angle2:
        angle_diff = angle2 - angle1
    else:
        angle_diff = angle1 - angle2
        
    if angle_diff > pi:
        angle_diff = (2*pi) - angle_diff
    
    return round(angle_diff, DECIMAL_PRECISION)

def angle_between_vectors(start_point, middle_point, end_point):
    """
    Calculate the smallest angle of two joined vectors.
    
    This assumes the two vectors share a point at `middle_point`,
    so can be described by the three points start, center, and end. 
    
    Parameters
    ----------
    start_point : Point or tuple
        A shapely Point object or (x,y) tuple
    middle_point : Point or tuple
        A shapely Point object or (x,y) tuple
    end_point : Point or tuple
        A shapely Point object or (x,y) tuple

    Returns
    -------
    float
        Angle in radians in the range (0,Pi)

    """
    angle1 = angle_between_points(middle_point, start_point)
    angle2 = angle_between_points(middle_point, end_point)
    
    return angle_diff(angle1, angle2)

def point_from_angle_and_distance(ref_point, angle, distance, use_radians=False):
    """
    Generate a new point with the specified angle and distance from ref_point.
    
    Angle is relative to the positive x-axis and should be in the 
    range (-pi,pi) for radians and (-180,180) for degrees.

    Parameters
    ----------
    ref_point : Point or tuple
        A shapely point object or (x,y) tuple
    angle : float
        Angle, relative to the positive x-axis, to make the new point. Either
        degrees or radians, specified by use_radians.
    distance : float
        Distance from ref_point for new point.
    use_radians : bool, optional
        Whether angle is radians. The default is False.

    Returns
    -------
    point
        shapely.geometry.Point

    """
    if isinstance(ref_point, Point):
        x1, y1 = ref_point.x, ref_point.y
    elif isinstance(ref_point, tuple):
        x1, y1 = ref_point
    else:
        raise TypeError('ref_point must be shapely.geometry.Point or (x,y) tuple')

    if not use_radians:
        angle = degrees_to_radians(angle)
        
    x_off = cos(angle) * distance
    y_off = sin(angle) * distance
    
    x_off = round(x_off, DECIMAL_PRECISION)
    y_off = round(y_off, DECIMAL_PRECISION)
    
    return Point((x1 + x_off, y1 + y_off))
    
    
def perpendicular_line_at_endpoint(ref_line, length, location='end', attached = 'center'):
    """
    Generate a new line segment which is perpendicular to a reference line.

    ref_line must have at least 1 segment. If more than 1 segment the perpendicular
    angle is calculated based on `location`.
    If location is 'end' then the new line will be perpendicular to the final
    segment of ref_line.
    If location is 'start' then the new line will be perpenducilar to the first
    segment of ref_line.
    
    The new line will intersect with either the start or end of the
    ref_line, depending on `location`.
    If `attached=center` the new line will have the ref_line endpoint as
    it's center.
    If `attached` is right or left, then the new line will have either its 
    right or left endpoints on the ref_line endpoint. Where, if the new line
    is centered, 'left' is the point counter-clockwise from the ref_line, and 
    'right' is the endpoint clockwise from ref_line.  

    Parameters
    ----------
    ref_line : LineString
        Shapely line with at least 2 points.
    length : float
        Length of the new line.
    location : str
        Either 'start' or 'end' for which line segment ref_line to calculate
        the 90 degree angle from.

    Returns
    -------
    new_line : LineString
        shapely LineString

    """
    if not isinstance(ref_line, LineString):
        raise TypeError('ref_line must be shapely LineString')
        
    # New perpendicular line will intersect at coord2
    if location == 'end':
        coord1 = ref_line.coords[-2]
        coord2 = ref_line.coords[-1] 
    elif location == 'start':
        coord1 = ref_line.coords[1]
        coord2 = ref_line.coords[0]
    else:
        raise ValueError('location must be start or end')
    
    if attached == 'center':
        first_point_distance = length/2
        second_point_distance = length/2
    elif attached == 'left':
        first_point_distance = 0
        second_point_distance = length
    elif attached == 'right':
        first_point_distance = length
        second_point_distance = 0
    else:
        raise ValueError('attached must be left,right, or center')
    
    ref_line_angle = angle_between_points(coord1, coord2) # in radians
    
    first_point = point_from_angle_and_distance(
        ref_point = coord2,
        angle = ref_line_angle + (pi/2),
        distance = first_point_distance,
        use_radians=True
        )
    second_point = point_from_angle_and_distance(
        ref_point = coord2,
        angle = ref_line_angle - (pi/2),
        distance = second_point_distance,
        use_radians=True
        )

    return LineString([first_point, second_point])
    

def perpendicular_line_at_midpoint(ref_line, length, location='end', attached = 'center'):
    """
    Generate a new line segment which is perpendicular to a reference line with 3 points.

    Given a ref_line of 2 segments, this will generate a new line which
    intersects the midpoint at an angle which is the average of the 2 adjacent
    segment angles. 

    ref_line must have at least 2 segment. If more than 2 segment the perpendicular
    angle is calculated based on `location`.
    If location is 'end' then the new line will be perpendicular to the final 2
    segments of ref_line.
    If location is 'start' then the new line will be perpenducilar to the first 2
    segment of ref_line.
    
    The new line will intersect with either the start or end of the
    ref_line, depending on `location`.
    If `attached=center` the new line will have the ref_line endpoint as
    it's center.
    If `attached` is right or left, then the new line will have either its 
    right or left endpoints on the ref_line endpoint. Where, if the new line
    is centered, 'left' is the point counter-clockwise from the ref_line, and 
    'right' is the endpoint clockwise from ref_line.  

    Parameters
    ----------
    ref_line : LineString
        Shapely line with at least 2 segments (e.g. >= 3 coordinates).
    length : float
        Length of the new line.
    location : str
        Either 'start' or 'end' for which line segment ref_line to calculate
        the 90 degree angle from.

    Returns
    -------
    new_line : LineString
        shapely LineString

    """
    if not isinstance(ref_line, LineString):
        raise TypeError('ref_line must be shapely LineString')
    if len(ref_line.coords) <= 2:
        raise ValueError('ref_line must have at least 2 segments')
    
    # New perpendicular line will intersect at coord2
    # coord3 is the line endpoint or startpoint
    if location == 'end':
        coord1 = ref_line.coords[-3]
        coord2 = ref_line.coords[-2] 
        coord3 = ref_line.coords[-1]
    elif location == 'start':
        coord1 = ref_line.coords[2]
        coord2 = ref_line.coords[1]
        coord3 = ref_line.coords[0]
    else:
        raise ValueError('location must be start or end')
    
    if attached == 'center':
        first_point_distance = length/2
        second_point_distance = length/2
    elif attached == 'left':
        first_point_distance = 0
        second_point_distance = length
    elif attached == 'right':
        first_point_distance = length
        second_point_distance = 0
    else:
        raise ValueError('attached must be left,right, or center')
    
    ref_line_angle1 = angle_between_points(coord1, coord2) # in radians
    ref_line_angle2 = angle_between_points(coord2, coord3)
    ref_line_angle_avg = (ref_line_angle1 + ref_line_angle2) /2
    
    first_point = point_from_angle_and_distance(
        ref_point = coord2,
        angle = ref_line_angle_avg + (pi/2),
        distance = first_point_distance,
        use_radians=True
        )
    second_point = point_from_angle_and_distance(
        ref_point = coord2,
        angle = ref_line_angle_avg - (pi/2),
        distance = second_point_distance,
        use_radians=True
        )

    return LineString([first_point, second_point])
