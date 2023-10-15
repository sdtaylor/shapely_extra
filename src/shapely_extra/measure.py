import numpy as np
from shapely.geometry import Point, LineString

from scipy import spatial

from shapely_extra.random import sample_points_on_line
from shapely_extra.angles import perpendicular_line_at_endpoint

        
def major_axis(polygon, n_sample_points=100, seed=1):
    """
    Generate a LineString representing the major axis of a polygon.
    
    This is calculated by densifying the boundary of the  polygon 
    with numerous points, measuring the pairwise euclidean distance 
    between them all, and choosing the longest. 

    Parameters
    ----------
    polygon : Polygon|MultiPolygon
        Shape to calculate the major axis for.
    n_sample_points : int
        Number of points along the polygon exterior to estimate the major
        axis from.
    seed : numeric
        Seed for the random locations of the exterior points. Set to None
        for no seed.

    Returns
    -------
    LineString.
        
    """
    
    if polygon.geom_type=='MultiPolygon':
        subpolygons_as_lines = [LineString(p.exterior.coords) for p in polygon.geoms]
        # Each subpolygon gets n points proportional to it's length, with
        # at least 1 point per subpolygon.
        subpolygon_line_lengths = [l.length for l in subpolygons_as_lines]
        total_length = sum(subpolygon_line_lengths)
        points_per_subpolygon = [max(int(length/total_length*n_sample_points),1) for length in subpolygon_line_lengths]
        
        exterior_point_arr = []
        for line, n_points in zip(subpolygons_as_lines, points_per_subpolygon):
            points = sample_points_on_line(line, n=n_points, ordered=True, seed=seed)
            exterior_point_arr.extend([(p.x,p.y) for p in points])
            
    elif polygon.geom_type=='Polygon':
        points = sample_points_on_line(LineString(polygon.exterior.coords), n=n_sample_points, ordered=True, seed=seed)
        exterior_point_arr = [(p.x,p.y) for p in points]
    
    else:
        raise TypeError('polygon must be either MultiPolygon or Polygon')
    
    
    distances = spatial.distance.pdist(exterior_point_arr)
    # Convert from condensed pairwise distance matrix to traditional one.
    distances =  spatial.distance.squareform(distances)
    
    # np.where gives us the indices of the longest distances
    # separated by axis. Here it is axis 0 and 1 for the
    # 2d distance matrix.
    max_0, max_1 = np.where(distances==distances.max())
    point1 = exterior_point_arr[max_0[0]]
    point2 = exterior_point_arr[max_1[0]]
    
    return LineString([point1, point2])

def _linestring_intersect_and_merge(l, polygon):
    """ 
    Intersect a line with a polygon and, if needed, stitch the
    a MultiLineString back together into a single LineString
    """
    assert l.geom_type=='LineString'
    out = l.intersection(polygon)
    if out.geom_type =='LineString':
        return out
    elif out.geom_type =='MultiLineString':
        first_point = out.geoms[0].coords[0]
        last_point  = out.geoms[-1].coords[-1]
        return LineString([first_point, last_point])
    else:
        return out
    

def minor_axis(polygon, major_axis_line=None, n_sample_points=100, seed=1):
    """
    Generate a LineString representing the minor axis of a polygon.

    Parameters
    ----------
    polygon : Polygon|MultiPolygon
        Shape to calculate the major axis for.
    major_axis : LineString, optional
        The major axis of polygon. If None, the default, this is caclucated
        automatically.
    n_sample_points : int
        Number of points along the major axis to estimate the minor
        axis from.
    seed : numeric
        Seed for the random locations of the exterior points. Set to None
        for no seed.


    Returns
    -------
    LineString.

    """
    # sample along major_axis step size
    # make perpinduclar line at each step 
    # cut to polygon (gotta make sure to not slice line in 2)
    # pick longest length
    # get perpindicular line
    
    if major_axis_line is not None:
        if not isinstance(major_axis_line, LineString):
            raise TypeError('major_axis must be a LineString')
    else:
        major_axis_line = major_axis(polygon, n_sample_points=n_sample_points, seed=seed)
    
    candidate_line_points = sample_points_on_line(major_axis_line, n=n_sample_points, ordered=True, seed=seed)
    candinate_line_start_length = max(
        polygon.bounds[2] - polygon.bounds[0],
        polygon.bounds[3] - polygon.bounds[1]
        )
    major_axis_startpoint = Point(major_axis_line.coords[0])
    candidate_lines = []

    for p in candidate_line_points:
        candidate_lines.append(perpendicular_line_at_endpoint(
            ref_line = LineString([major_axis_startpoint, p]), 
            length = candinate_line_start_length, 
            location='end', 
            attached = 'center'
            ))
        
        candidate_lines[-1] = _linestring_intersect_and_merge(candidate_lines[-1],polygon)
        
    candidate_line_lengths = [l.length for l in candidate_lines]
    
    return candidate_lines[np.argmax(candidate_line_lengths)]