from shapely.geometry import Point, LineString

from shapely_extra.angles import angle_between_points, point_from_angle_and_distance

from typing import Union

def extend_line(line:LineString, 
                length: Union[float,None] = None, 
                length_frac: Union[float,None] = None, 
                side:str = 'both') -> LineString:
    """
    Extend a line past it's endpoints. Either by an absolute value using
    length, or a fraction of the lines current length using length_frac.
    
    The extension is either at the beginning or end of the line, specified by
    side. If side='both', then both sides are each extended by half of the desired
    length. The extension will be parallel to the 2 points comprising the line
    at the respective end or start. In this way, a perfectly strait line
    will stay straight. 

    Parameters
    ----------
    line : LineString
        The line to extend.
    length : numeric, optional
        The absolute lenght to extend. Ignored if length_frac is specified. 
        The default is None.
    length_frac : numeric, optional
        The fraction to extend by. The final length will be 
            line.length * (1 + length_frac).
        Thus, with length_frac = 1, the total line length will double. With
        length_frac = 0.5, the total line length will increase by 50%.
    side : str, optional
        Which side of the line to add length onto. 'start', 'end', or 'both'.
        If both, the length added will be split evenly between start and end. 
        The default is 'both'.

    Returns
    -------
    LineString.

    """
    if not isinstance(line, LineString):
        raise ValueError('line must be LineString')
    
    if side not in ['start','end','both']:
        raise ValueError('side must be start, end, or both')
        
    if length_frac is not None:
        length = line.length * length_frac
    else:
        if length is None:
            raise ValueError('length or length_frac must be specified')
            
    if length <= 0:
        raise ValueError('length or length_frac must be  > 0')
    
    if side == 'both':
        length = length/2
    
    line_coords = list(line.coords)
    
    if side in ['start','both']:
        old_start = line_coords[0]
        ref_point = line_coords[1]
        
        a = angle_between_points(ref_point, old_start)
        new_start = point_from_angle_and_distance(
                ref_point   = old_start,
                angle       = a,
                distance    = length,
                use_radians = True
            )
        
        line_coords.insert(0, new_start)
    
    if side in ['end','both']:
        old_end   = line_coords[-1]
        ref_point = line_coords[-2]
        
        a = angle_between_points(ref_point, old_end)
        new_end = point_from_angle_and_distance(
                ref_point   = old_end,
                angle       = a,
                distance    = length,
                use_radians = True
            )
    
        line_coords.append(new_end)

    return LineString(line_coords)        
        
        