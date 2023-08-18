from shapely_extra.angles import (
        radians_to_degrees,
        degrees_to_radians,
        angle_between_points,
        angle_diff,
        angle_between_vectors,
        point_from_angle_and_distance,
        perpendicular_line_at_endpoint,
        )

from shapely.geometry import Point, LineString
from random import choices
from math import isclose


def test_rad_to_deg():
    degrees = list(range(-180,180,1))
    radians = [degrees_to_radians(d) for d in degrees]
    match = [isclose(d,radians_to_degrees(r)) for d, r in zip(degrees,radians)]
    assert all(match)

def test_angleBetweenPoints_input():
    """A shapely point and tuple should have the same results"""
    ints = range(0,1000)
    k=500
    points1 = [Point(x,y) for x,y in zip(choices(ints,k=k),choices(ints,k=k))]
    points2 = [Point(x,y) for x,y in zip(choices(ints,k=k),choices(ints,k=k))]

    matches = [angle_between_points(p1,p2) == angle_between_points((p1.x,p1.y),(p2.x,p2.y)) for p1, p2 in zip(points1,points2)]
    print(matches)
    assert all(matches)

def test_angleBetweenPoints():
    """Input angle for newly generated point should match resulting measured angle"""
    angles = list(range(-179,181,1))
    angles.extend([a/10 for a in angles]) # add some float angles as well
    point = Point(0,0)
    distance = 10
    new_points = [point_from_angle_and_distance(point, angle=a, distance=distance, use_radians=False) for a in angles]
    new_angles = [angle_between_points(point, new_p) for new_p in new_points]
    new_angles = [radians_to_degrees(a) for a in new_angles]
    matches = [isclose(angle, new_angle, rel_tol=1e-5) for angle,new_angle in zip(angles, new_angles)]

    assert all(matches)

def test_angleBetweenPoints_around_circle():
    """Points placed equal angles around a circle should have the same distance"""
    dist = 5
    center = Point(0,0)
    right  = point_from_angle_and_distance(center, angle=0, distance=dist, use_radians=False)
    top    = point_from_angle_and_distance(center, angle=90, distance=dist, use_radians=False)
    left   = point_from_angle_and_distance(center, angle=180, distance=dist, use_radians=False)
    bottom = point_from_angle_and_distance(center, angle=-90, distance=dist, use_radians=False)

    top_matches = isclose(top.distance(left), top.distance(right))
    bottom_matches = isclose(bottom.distance(left), bottom.distance(right))
    left_matches = isclose(left.distance(top), left.distance(bottom))
    right_matches = isclose(right.distance(top), right.distance(bottom))

    assert all([top_matches, bottom_matches, left_matches, right_matches])
    
def test_perpendicular_angle():
    """Angle of new perpendicular line should be 90"""
    line = LineString([(0,0),(5,10)])
    new_line = perpendicular_line_at_endpoint(line, length=10, location='end', attached='center')

    # New line consists of 2 points. both of which should be 90 deg. relative to endpoint.
    new_angle1 = angle_between_vectors(line.coords[0], line.coords[1], new_line.coords[0])
    new_angle2 = angle_between_vectors(line.coords[0], line.coords[1], new_line.coords[1])
    new_angle1 = radians_to_degrees(new_angle1)
    new_angle2 = radians_to_degrees(new_angle2)
    # Rounding errors will happen, but this should hit 90 degrees within a pretty small tolerance
    assert all([isclose(new_angle1,90, rel_tol=1e-5), isclose(new_angle2, 90.,rel_tol=1e-5)])

def test_perpendicular_length():
    """Length of new perpendicular line should match input length"""
    lengths = list(range(1,20,1))
    lengths.extend([l/10 for l in lengths])
    line = LineString([(0,0),(5,10)])
    new_lines = [perpendicular_line_at_endpoint(line, length=l, location='end', attached='center') for l in lengths]
    lines_match = [isclose(length,new_line.length,rel_tol=1e-5) for length, new_line in zip(lengths, new_lines)]

    assert all(lines_match)
