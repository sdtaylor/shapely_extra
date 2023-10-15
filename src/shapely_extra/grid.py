import numpy as np

from shapely_extra import shapes
from shapely.geometry import box, Point
from shapely.affinity import translate
from shapely.ops import snap

from math import ceil, sqrt, pi

def point_grid(polygon, distance=1):
    """
    Create a point grid contained within a polygon.

    Parameters
    ----------
    polygon : Polygon|MultiPolygon
        The shape within which to fill with points.
    distance : numeric, optional
        The distance between points on both the  x and y axis. The default is 1.

    Returns
    -------
    [Point]

    """
    minx, miny, maxx, maxy = polygon.bounds
    
    all_y, all_x = np.meshgrid(
            np.arange(miny, maxy, distance),
            np.arange(minx, maxx, distance)
            )
    
    points = []
    for x, y in zip(all_x.flatten(), all_y.flatten()):
        points.append(
            Point(x, y)
            )
    
    return [p for p in points if p.within(polygon)]

def square_grid(polygon, square_sidelength=1, square_area=None, clip=False):
    """
    Generate a square grid within a polygon. 

    Parameters
    ----------
    polygon : Polygon|MultiPolygon
        The shape within which to fill with a square grid.
    square_sidelength : numeric, optional
        The length of 1 side of the square. Ignored if area is specified.
    square_area : numeric, optional
        Desired area of the square. The default is None.
    clip : bool, optional
        If True then grid elements crossing the polygon boundary will be clipped to
        the boundary. The default is False.

    Returns
    -------
    [Polygon].

    """
    if square_area is not None:
        square_sidelength = sqrt(square_area)
    
    # Buffer by the internal spacing to ensure the grid is generated all along the boundary.
    centers = point_grid(polygon = box(*polygon.buffer(square_sidelength).bounds), distance=square_sidelength)
    
    squares = [shapes.square(center=(c.x,c.y), sidelength=square_sidelength) for c in centers]
    squares = [s for s in squares if s.intersects(polygon)]
    if clip:
        squares = [s.intersection(polygon) for s in squares]
    
    return squares

# A circle grid looks neat, but is there a use case since it can't fill up
# a polygon completly?

# def circle_grid(polygon, circle_radius=1, circle_circumference=None, circle_area=None, circle_tolerance=0.1, clip=False):
#     """
#     Generate a circle grid within a polygon. Note that there will be gaps
#     between the circles and it will not fill the polygon completely.

#     Parameters
#     ----------
#     polygon : Polygon|MultiPolygon
#         The shape within which to fill with a circle grid.
#     circle_radius : numeric, optional
#         The desired radius of the circle. Ignored if area is specified.
#     circle_circumference : numeric, optional
#         The desirec circumference of the circule.
#     circle_area : numeric, optional
#         The desired area of the circle. 
#     circle_tolerance : numeric, optional
#         How close to the true circle area. This is the absolute tolerance. So
#         for example with tolerance=10, the  derived area of the returned circle
#         will be ± 10 units to the true area.  
#         The default is 0.1 units.
#     clip : bool, optional
#         If True then grid elements crossing the polygon boundary will be clipped to
#         the boundary. The default is False.

#     Returns
#     -------
#     [Polygon].

#     """
#     base_circle = shapes.circle(
#             radius = circle_radius,
#             circumference = circle_circumference,
#             area = circle_area,
#             tolerance = circle_tolerance
#         )
    
#     base_radius = sqrt(base_circle.area / pi)
    
#     circle_centers = point_grid(polygon = box(*polygon.bounds), distance=base_radius*2)
#     circles = []
#     for center in circle_centers:
#         circles.append( 
#             translate(base_circle, xoff=center.x, yoff=center.y)
#             )
        
#     circles = [c for c in circles if c.intersects(polygon)]
#     if clip:
#         squares = [c.intersection(polygon) for c in circles]

_is_even = lambda x: x % 2 == 0
_is_odd  = lambda x: x % 2 != 0

def hexagon_grid(polygon, hexagon_sidelength=1, hexagon_area=None, clip=False):
    '''
    Generate a hexagon grid contained within a polygon.
    
    From https://www.redblobgames.com/grids/hexagons/

    Parameters
    ----------
    polygon : Polygon|MultiPolygon
        The shape within which to fill with a circle grid.
    hexagon_sidelength : numeric, optional
        Length of each edge of the hexagon. Ignored if area is specified.
    hexagon_area : numeric, optional
        The desired area of the hexagon. The required sidelength will
        be calculated.
    clip : TYPE, optional
        DESCRIPTION. The default is False.

    Returns
    -------
    [Polygon]

    '''
    if hexagon_area is not None:
        hexagon_sidelength = sqrt( (hexagon_area*2) /  (3*sqrt(3)) )
    
    # Buffer by the internal spacing to ensure the grid is generated all along the boundary.
    minx, miny, maxx, maxy = polygon.buffer(hexagon_sidelength).bounds
    
    # x axis increases with columns
    # y axis increases with rows
    
    x_spacing = hexagon_sidelength*(3/2)
    y_spacing = hexagon_sidelength*sqrt(3) 

    n_cols = ceil((maxx-minx)/x_spacing)
    n_rows = ceil((maxy-miny)/y_spacing)
    
    hexagons = []
    hexagon_ids = [] # for debugging
    for row_i in range(n_rows):
        hexagons.append([None]*n_cols)       
        hexagon_ids.append([None]*n_cols)
        for col_i in range(n_cols):
            if _is_odd(col_i):
                col_x_offset = x_spacing * col_i
                col_y_offset = (y_spacing*0.5)  + (row_i * y_spacing)
            else:
                col_x_offset = x_spacing * col_i
                col_y_offset = y_spacing  * row_i
            
        
            hexagon_ids[row_i][col_i] = f'({row_i},{col_i})'
            
            hexagons[row_i][col_i] = shapes.hexagon(
                center = (minx + col_x_offset, miny + col_y_offset),
                sidelength = hexagon_sidelength,
                )
            
    #-------------
    # Rounding errors means hexagon edges are not exactly aligned by some very
    # small numbers. So iterate though each hexagon's neighbors and snap
    # them together.
    # Using the offset grid neighboor method from 
    # https://www.redblobgames.com/grids/hexagons/#neighbors-offset
    evenq_direction_differences = [
        # even cols 
        [[+1, +1], [+1,  0], [ 0, -1], 
         [-1,  0], [-1, +1], [ 0, +1]],
        # odd cols 
        [[+1,  0], [+1, -1], [ 0, -1], 
         [-1, -1], [-1,  0], [ 0, +1]],
    ]
    
    snapping_tolerance = hexagon_sidelength*0.01
    for row_i in range(n_rows):
        for col_i in range(n_cols):
            target_hex_shape = hexagons[row_i][col_i]
            for neighbor in range(6):
                parity = col_i & 1
                diffs = evenq_direction_differences[parity][neighbor]
                try:
                    neighbor_hex_shape = hexagons[row_i + diffs[0]][col_i + diffs[1]]
                    hexagons[row_i + diffs[0]][col_i + diffs[1]] = snap(neighbor_hex_shape, target_hex_shape, snapping_tolerance)
                except IndexError:
                    # beyond the grid
                    pass
    
    #--------------
    # Flatten the grid
    hexagons = [i for row in hexagons for i in row]
    
    # Subset to shapes which are at least partly within polygon.
    hexagons = [i for i in hexagons if i.intersects(polygon)]

    if clip:
        hexagons = [s.intersection(polygon) for s in hexagons]
    
    return [h for h in hexagons if not h.is_empty]
