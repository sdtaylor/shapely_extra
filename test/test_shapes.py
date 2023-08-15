from shapely_extra import shapes

from math import pi, sqrt

import pytest


def test_hexagon_area1():
    initial = shapes.hexagon(sidelength=100)
    with_area = shapes.hexagon(area=initial.area)
    assert with_area.area == pytest.approx(initial.area)

def test_hexagon_area2():
    sidelength = 10
    true_area = ( 3 * sqrt(3) *  (sidelength**2)) / 2
    derived_area = shapes.hexagon(sidelength=sidelength).area
    assert derived_area == pytest.approx(true_area)

def test_hexagon_centroid1():
    center = (123,123)
    initial = shapes.hexagon(center=center , sidelength=100)
    derived_center = (initial.centroid.x, initial.centroid.y)
    assert derived_center == pytest.approx(center)
    
def test_hexagon_centroid2():
    center = (-500,-500)
    initial = shapes.hexagon(center=center , area=100)
    derived_center = (initial.centroid.x, initial.centroid.y)
    assert derived_center == pytest.approx(center)

def test_circle_area1():
    radius = 1000
    true_area = pi * radius**2
    derived_area = shapes.circle(radius=radius, tolerance=0.1).area
    assert derived_area == pytest.approx(true_area, abs=0.1)

def test_circle_area2():
    radius = 0.01
    true_area = pi * radius**2
    derived_area = shapes.circle(radius=radius, tolerance=1e-8).area
    assert derived_area == pytest.approx(true_area, abs=1e8)

def test_circle_centroid1():
    center = (123,123)
    initial = shapes.circle(center=center , area=100)
    derived_center = (initial.centroid.x, initial.centroid.y)
    assert derived_center == pytest.approx(center)
    
def test_circle_centroid2():
    center = (-500,-500)
    initial = shapes.circle(center=center , circumference=100)
    derived_center = (initial.centroid.x, initial.centroid.y)
    assert derived_center == pytest.approx(center)


def test_square_area1():
    length = 1000
    true_area = length**2
    derived_area = shapes.square(sidelength=length).area
    assert derived_area == pytest.approx(true_area, abs=0.1)

def test_square_area2():
    length = 1/1e6
    true_area = length**2
    derived_area = shapes.square(sidelength=length).area
    assert derived_area == pytest.approx(true_area)

def test_square_centroid1():
    center = (123,123)
    initial = shapes.square(center=center, area=100)
    derived_center = (initial.centroid.x, initial.centroid.y)
    assert derived_center == pytest.approx(center)
    
def test_square_centroid2():
    center = (-500,-500)
    initial = shapes.square(center=center, sidelength=100)
    derived_center = (initial.centroid.x, initial.centroid.y)
    assert derived_center == pytest.approx(center)
