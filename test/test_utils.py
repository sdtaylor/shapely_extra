from shapely.geometry import Point, LineString

from shapely_extra.utils import extend_line

import pytest

def test_extend_line_end():
    """ Last point should be the same if side='start'"""
    l = LineString([Point(-1,-1), Point(1,1)])
    
    l2 = extend_line(l, length_frac=0.5, side='start')

    end_is_the_same = l.coords[-1] == l2.coords[-1]
    start_is_changed = l.coords[0] != l2.coords[0]
    assert end_is_the_same and start_is_changed

def test_extend_line_start():
    """ First point should be the same if side='end'"""
    l = LineString([Point(-1,-1), Point(1,1)])
    
    l2 = extend_line(l, length_frac=0.5, side='end')

    start_is_the_same = l.coords[0] == l2.coords[0]
    end_is_chaged     = l.coords[-1] != l2.coords[-1]
    assert start_is_the_same and end_is_chaged

def test_extend_line_length1():
    """new length is longer and the same for all 3 side options"""
    l = LineString([Point(-1,-1), Point(1,1)])
    
    new_lines = []
    for s in ['start','end','both']:
        new_lines.append(extend_line(
            l,
            length_frac = 1,
            side=s
            ))

    new_length = l.length * 2
    
    assert all([
        new_l.length == pytest.approx(new_length)
        for new_l in new_lines
        ])