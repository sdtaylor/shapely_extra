from shapely_extra.random import (
    sample_points_in_polygon,
    sample_points_on_line,
    sample_polygons,
    )
from shapely_extra import shapes

from shapely.ops import unary_union

import pytest

# add execution_number to some tests so they are repeated several times.
# These are each a little different due to random number generation.
@pytest.mark.parametrize('execution_number', range(5))
def test_random_points_within_polygon1(execution_number):
    """Correct n is returned"""
    polygon = shapes.hexagon((10,10), area=100)
    points = sample_points_in_polygon(polygon, n=500)
    assert len(points) == 500

@pytest.mark.parametrize('execution_number', range(5))
def test_random_points_within_polygon2(execution_number):
    """All points within original polygon"""
    polygon = shapes.hexagon((10,10), area=100)
    points = sample_points_in_polygon(polygon, n=500)
    assert all([p.within(polygon) for p in points])

def test_random_points_within_polygon3():
    """Setting the seed results in the same points"""
    polygon = shapes.hexagon((10,10), area=100)
    points1 = sample_points_in_polygon(polygon, n=500, seed=100)
    points2 = sample_points_in_polygon(polygon, n=500, seed=100)
    assert all([a==b for a,b in zip(points1, points2)])

def test_random_points_within_polygon4():
    """Setting different seeds results in the different points"""
    polygon = shapes.hexagon((10,10), area=100)
    points1 = sample_points_in_polygon(polygon, n=500, seed=100)
    points2 = sample_points_in_polygon(polygon, n=500, seed=101)
    assert not all([a==b for a,b in zip(points1, points2)])

@pytest.mark.parametrize('execution_number', range(5))
def test_random_polygons1(execution_number):
    """correct n is returned"""
    original_polygon = shapes.square((10,10), area=100)
    new_polygons = sample_polygons(original_polygon, n=500)
    assert len(new_polygons) == 500

@pytest.mark.parametrize('execution_number', range(5))
def test_random_polygons2(execution_number):
    """New polygon total area approximates original"""
    original_polygon = shapes.square((10,10), area=100)
    new_polygons = sample_polygons(original_polygon, n=500)
    original_area = original_polygon.area
    new_area      = unary_union(new_polygons).area
    assert new_area == pytest.approx(original_area)

@pytest.mark.parametrize('execution_number', range(5))
def test_random_polygons3(execution_number):
    """New polygon total area == sum of individual area."""
    original_polygon = shapes.square((10,10), area=100)
    new_polygons = sample_polygons(original_polygon, n=500)
    union_area      = unary_union(new_polygons).area
    summed_area     = sum([p.area for p in new_polygons])
    assert union_area == pytest.approx(summed_area)

def test_random_polygons4():
    """Setting the seed results in the same polygons"""
    original_polygon = shapes.square((10,10), area=100)
    new_polygons1 = sample_polygons(original_polygon, n=500, seed=100)
    new_polygons2 = sample_polygons(original_polygon, n=500, seed=100)
    assert all([a==b for a,b in zip(new_polygons1, new_polygons2)])

def test_random_polygons5():
    """Setting different seeds results in different polygons"""
    original_polygon = shapes.square((10,10), area=100)
    new_polygons1 = sample_polygons(original_polygon, n=500, seed=100)
    new_polygons2 = sample_polygons(original_polygon, n=500, seed=101)
    assert not all([a==b for a,b in zip(new_polygons1, new_polygons2)])
