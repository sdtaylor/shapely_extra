from shapely_extra import measure, shapes, angles
from shapely.ops import unary_union, split

import pytest

test_shape = unary_union([shapes.circle(center=(i, 0), radius=3) for i in [0,5,10,15,20,25]])

@pytest.mark.parametrize('n_points', [50,100,200,500])
def test_major_axis1(n_points):
    """ 
    With the seed and sample points set, the returned line should be the
    same every time.
    """
    line1 = measure.major_axis(test_shape, n_sample_points = n_points, seed=5)
    line2 = measure.major_axis(test_shape, n_sample_points = n_points, seed=5)
    assert line1 == line2
    
def test_major_axis2():
    """ 
    With different seeds, the axis should be a tad different every time.
    Although functionally they might be the same.
    """
    line1 = measure.major_axis(test_shape, seed=5)
    line2 = measure.major_axis(test_shape, seed=6)
    assert line1 != line2

@pytest.mark.parametrize('n_points', [50,100,200,500])
def test_minor_axis1(n_points):
    """ 
    As long as the seed and n_sample_points are specified, the the minor
    axis should be the same whether or not the initial major axis line
    is passed
    """
    major_axis_line = measure.major_axis(test_shape, n_sample_points = n_points, seed=5)
    minor_axis_line1 = measure.minor_axis(test_shape, major_axis_line = major_axis_line, n_sample_points = n_points, seed=5)
    minor_axis_line2 = measure.minor_axis(test_shape, major_axis_line = None,            n_sample_points = n_points, seed=5)
    assert minor_axis_line1 == minor_axis_line2

def test_minor_axis2():
    """
    The minor axis should always perpindicular to the major axis
    """
    major_axis_line = measure.major_axis(test_shape)
    minor_axis_line = measure.minor_axis(test_shape, major_axis_line = major_axis_line)
    
    line_intersection = major_axis_line.intersection(minor_axis_line)
    
    a = angles.angle_between_vectors(
        start_point = major_axis_line.coords[0],
        middle_point = (line_intersection.x, line_intersection.y),
        end_point    = minor_axis_line.coords[0]
        )
    
    assert angles.radians_to_degrees(a) == pytest.approx(90)
