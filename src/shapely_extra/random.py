import numpy as np
from shapely.geometry import Point, Polygon, MultiPolygon, MultiPoint, LineString
from shapely.ops import unary_union, voronoi_diagram
from shapely import line_interpolate_point

from shapely_extra import shapes

from typing import Union

def sample_points_in_polygon(polygon: Union[Polygon, MultiPolygon], 
                             n:int, 
                             seed: Union[float,None] = None, 
                             attempt:int = 1) -> list[Point]:
    """
    Return n randomly located points within a Polygon.
    
    Parameters
    ----------
    poly : Polygon or MultiPolygon
        DESCRIPTION.
    n : int
        Number of points to calculate. 
    seed : numeric
        Random seed.
    attempts : int
        To keep the recursive function under control.

    Returns
    -------
    [Point]
        List of Points.

    """
    if attempt > 50:
        raise RuntimeError(f'attempts exceeded, cannot sample polygon')
    assert polygon.geom_type in ['Polygon','MultiPolygon']

    rng = np.random.default_rng(seed)
    
    minx, miny, maxx, maxy = polygon.bounds
    
    x_coords = rng.uniform(low = minx, high=maxx, size=n*2)
    y_coords = rng.uniform(low = miny, high=maxy, size=n*2)
    point_geoms = [Point(x,y) for x,y in zip(x_coords, y_coords)]
    
    point_geoms = [p for p in point_geoms if p.within(polygon)]
    
    while len(point_geoms) < n:
        point_geoms.extend(
            sample_points_in_polygon(polygon, n, seed, attempt+1)
            )

    return point_geoms[:n]


def sample_points_on_line(linestring:LineString, 
                          n:int, 
                          ordered:bool = False, 
                          seed: Union[float,None] = None) -> list[Point]:
    """
    Return n points randomly located along a line.

    Parameters
    ----------
    linestring : LineString
        Line to sample upon.
    n : int
        Number of points to sample.
    ordered : bool, optional
        Whether the points should be ordered, with the 1st point the closest
        to the linestring origin. The default is False.
    seed : numeric, optional
        Random seed. Use None, the default, for no seed. 

    Returns
    -------
    [Point]
        List of points.

    """
    assert linestring.geom_type in ['LineString']
    
    rng = np.random.default_rng(seed)
    point_lengths_from_origin = rng.uniform(low = 0, high=linestring.length, size=n)
    if ordered:
        point_lengths_from_origin.sort()
    return [line_interpolate_point(linestring, distance=d) for d in point_lengths_from_origin]

def sample_polygons(polygon: Union[Polygon, MultiPolygon], 
                    n:int, 
                    method:str = 'voronoi', 
                    seed: Union[float,None] = None) -> list[Polygon]:
    """
    Split a polygon into n random shapes. Currently only one method
    is supported. 

    Parameters
    ----------
    polygon : Polygon or MultiPolygon
        A polygon to split into n random shapes. 
        
        If you want to create random polygons within some bounds of
        (minx, miny, maxx, maxy) use shapely.geometry.box to create a
        polygon of the bounds first.
        
    n : int
        Number of new polygyons to randomly place within polygon.
        
    method : str
        voronoi
            Start with n points randomly located within the polygon. Then
            create a voronoi diagram intersected with the original polygon,
            producing n new shapes. 
        
    seed : numeric, optional
        Random seed. Use None, the default, for no seed. 

    Returns
    -------
    [Polygon].
        A list of polygons which fill the original polygon.
    """
    random_points = sample_points_in_polygon(
        polygon = polygon,
        n=n,
        seed=seed,
        )
    
    if method == 'voronoi':
        point_geom = MultiPoint(random_points)
        polygon_geoms = [g.intersection(polygon) for g in voronoi_diagram(point_geom).geoms]
        
        return polygon_geoms

    else:
        raise ValueError('No other methods configured besides voronoi')
    
    
    
    
    
    
    
    
    
    
    
    
    
    