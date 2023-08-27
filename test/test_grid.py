from shapely_extra import shapes
from shapely_extra import grid

from shapely.ops import unary_union

from math import pi, sqrt

from scipy.spatial import distance

import pytest

test_shape = shapes.circle(center=(100,100), radius=100)
primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]

def test_point_grid_counts():
    """
    A more dense point grid should contain more points.
    """
    grid1 = grid.point_grid(test_shape, distance=10)
    grid2 = grid.point_grid(test_shape, distance=8)
    
    assert len(grid2) > len(grid1)

@pytest.mark.parametrize('point_grid_distance', primes)
def test_point_grid_distance(point_grid_distance):
    """ Measured min distance should equal input"""
    points = grid.point_grid(test_shape, distance=point_grid_distance)
    
    points_xy = [[p.x, p.y] for p in points]
    
    derived_distances = distance.pdist(points_xy)
    
    assert point_grid_distance == pytest.approx(derived_distances.min())
    
@pytest.mark.parametrize('sidelength', primes)
def test_square_grid_inputs(sidelength):
    """ Equal sidelength/area should produce the same grid"""
    grid1 = grid.square_grid(test_shape, square_sidelength = sidelength)
    grid2 = grid.square_grid(test_shape, square_area = sidelength**2)
    
    n_polygons_match = len(grid1) == len(grid2)
    total_area_matches = sum([g.area for g in grid2]) == pytest.approx(sum([g.area for g in grid1]))
    assert all([n_polygons_match, total_area_matches])

@pytest.mark.parametrize('sidelength', primes)
def test_hexagon_grid_centers(sidelength):
    """ 
    Use a circle in all 4 quadrants, and in the center, to
    test the hex grid generation routine.
    """
    grid_polygons = []
    for center in [(0,0), (500,500), (-500,500), (-500,-500), (500,-500), (0,500), (500,0)]:
        grid_polygons.append(
            grid.hexagon_grid(shapes.circle(center=center, radius=100), hexagon_sidelength = sidelength)
            )
        
    grid_n_polygons = [len(g) for g in grid_polygons]
    grid_area       = [sum([p.area for p in g]) for g in grid_polygons]
    
    counts_match = all([grid_n_polygons[0] == n for n in grid_n_polygons])
    areas_matches = all([grid_area[0] == pytest.approx(a) for a in grid_area])

    assert all([counts_match, areas_matches])

@pytest.mark.parametrize('grid_method', [grid.square_grid, grid.hexagon_grid])
def test_grid_derived_area1(grid_method):
    """
    The clip method should ensure that the  total area of all grid
    elements is equal to the area of the original polygon
    """
    grid_shapes = grid_method(test_shape,5, clip=True)
    assert unary_union(grid_shapes).area == pytest.approx(test_shape.area)
    
@pytest.mark.parametrize('grid_method', [grid.square_grid, grid.hexagon_grid])
def test_grid_derived_area2(grid_method):
    """
    Sum of the area of all grid elements should equal to total area of the
    grid element union.
    This will fail with overlapping polygons within the grid.
    """
    grid_shapes = grid_method(test_shape,10, clip=True)
    area1 = sum([s.area for s in grid_shapes])
    area2 = unary_union(grid_shapes).area
    assert area1 == pytest.approx(area2)




