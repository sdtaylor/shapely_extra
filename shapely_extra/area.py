import numpy as np

import shapely.geometry
from shapely.geometry import box, MultiPolygon
from shapely.ops import unary_union

from scipy.sparse.csgraph import floyd_warshall
from scipy.sparse import csr_matrix
from scipy import optimize


class BlockSplitter:
    def __init__(self, 
                 polygon,
                 subpolygon_weights,
                 block_size=0.05):
        """
        

        Parameters
        ----------
        polygon : Polygon|MultiPolygon
            The initial shape to split into smaller polygons.
        subpolygon_weights : [float]
            List of floats representing the desired weighted area for each
            smaller polygon. Eg to split a polgyon in half use  [0.5,0.5].
            Weights must sum to 1
        block_size : float, optional
            The size of the grid shapes which will be used to construct
            smaller polygons. This is the fraction of the distance
            between polygon.bounds max and min values. 
            The default is 0.05.

        Returns
        -------
        None.

        """
        assert isinstance(polygon, shapely.geometry.base.BaseGeometry), 'polygon must be a shapely Polygon or Multipolygon'
        assert polygon.geom_type in ['Polygon','MultiPolygon'], 'polygon must be a shapely Polygon or Multipolygon'
               
        
        assert 0 < block_size < 1, 'block size must be between 0-1'
        self.block_size = block_size
        
        self.polygon  = polygon
        self.subpolygon_weights = subpolygon_weights
        self.n_splits = len(subpolygon_weights) -1
        
        self.optimized=False
        self.optimized_splits = None
        
    def final_shapes(self):
        if not self.optimized:
            raise RuntimeError('splits are not optimized')
            
        return self._make_shapes(splits_idx = self.optimized_splits)
    
    def prep_shape(self):        
        minx, miny, maxx, maxy = self.polygon.bounds
        block_size_x = (maxx - minx) * self.block_size
        block_size_y = (maxy - miny) * self.block_size
    
        self.grid_shapes = []
        full_grid = self._make_regular_grid(
            minx = minx, 
            miny = miny, 
            maxx = maxx,
            maxy = maxy,
            side_length = min([block_size_x, block_size_y]),
            )

        # Cut down the  full grid to only those grid elements within the  
        # polygon. Cropping them where needed so that all the grid elements
        # put together will equal the original polygon.
        for element in full_grid:
            element = element.intersection(self.polygon)
            if element.is_empty:
                continue 
            if element.geom_type=='Polygon':
                self.grid_shapes.append(element)
            elif element.geom_type=='MultiPolygon':
                self.grid_shapes.extend(element.geoms)
            else:
                raise RuntimeError(f'cant handle geom_type {element.geom_type}')
    
        adjacency_matrix = self._get_path_adjacency_matrix(self.grid_shapes)
    
        path_distances = floyd_warshall(csr_matrix(adjacency_matrix), return_predecessors=False)
        
        # Of all the pairwise grid elements, choose the pair with the
        # longest distance between them. Use the 1st of the pair as
        # a "start" for creating the split polygon.
        farthest_points = np.where(path_distances == path_distances.max())[0]
        start_shape_i = farthest_points[0]
        
        distance_from_start = path_distances[start_shape_i]
        self.element_spatial_order = list(range(len(self.grid_shapes)))
        self.element_spatial_order.sort(key = lambda i: distance_from_start[i])
        
        self.grid_shapes = [self.grid_shapes[i] for i in self.element_spatial_order]
    
    def _make_shapes(self, splits_idx):
        needed_split_points = self.n_splits
        if len(splits_idx) != self.n_splits:
            msg = f"need {self.n_splits} splits, got {splits_idx}"
            raise RuntimeError(msg)
        if not all([isinstance(i, int) for i in splits_idx]):
            raise RuntimeError('splits_idx must be integers')
        
        shapes = []
        begin_idx = 0
        for idx in splits_idx:
            shapes.append(unary_union(self.grid_shapes[begin_idx:idx]))
            begin_idx = idx 
        
        # The final sub polygon will always be from the last split_idx
        # until the end.
        shapes.append(unary_union(self.grid_shapes[begin_idx:]))
        
        return shapes
    
    def _calculate_area_weights(self, shapes):
        total_area = unary_union(shapes).area
        return np.array([s.area/total_area for s in shapes])
    
    def optimize_polygon_split(self):
        
        def func_to_minimize(x):
            x = [int(i) for i in x]
            candidate_shapes = self._make_shapes(splits_idx=x)
            candidate_weights = self._calculate_area_weights(candidate_shapes)
            return np.absolute(self.subpolygon_weights-candidate_weights).mean()

        n_grid_shapes = len(self.grid_shapes)
        bounds = [(0, n_grid_shapes) for i in range(self.n_splits)]
        
        # Linear constraint to specify that the optimizion solution
        # (the 1d array x) should be monotonically increasing such 
        # that x_0 < x_1 < x_2 ... < x_n.
        # Only needed when there is more  than 1 split.
        n_optimize_params = self.n_splits
        
        if n_optimize_params > 1:
            n_constraints = n_optimize_params - 1
            constraint_matrix = []
            for constraint_i in range(n_constraints):
                c = [0] * n_optimize_params
                c[constraint_i]   = 1
                c[constraint_i+1] = -1
                constraint_matrix.append(c)
            
            constraints = optimize.LinearConstraint(
                A = constraint_matrix,
                lb = [-np.inf] * n_constraints,
                ub = [-1] * n_constraints
                )
        else:
            constraints = () # no constraints
        
        # Using the weights to make some decent starting points
        n_grid_shapes = len(self.grid_shapes)
        initial_splits = (np.cumsum(self.subpolygon_weights[:-1]) * n_grid_shapes).astype(int)
        
        optimize_out = optimize.differential_evolution(
            func = func_to_minimize, 
            bounds = bounds,
            constraints = constraints,
            x0 = initial_splits
            )
        
        self.optimized_splits = [int(i) for i in optimize_out['x']]
        self.optimized = True
    
    def _make_regular_grid(self, minx, miny, maxx, maxy, side_length):
        all_y, all_x = np.meshgrid(
            np.arange(miny, maxy, side_length),
            np.arange(minx, maxx, side_length)
            )
        
        polygons = []
        for x, y in zip(all_x.flatten(), all_y.flatten()):
            polygons.append(
                box(x, y, x+side_length, y+side_length)
                )
        return polygons
        
    def _get_path_adjacency_matrix(self, elements):
        n_elements = len(elements)
        
        # First use an adjancy matrix to find the longest path while 
        # staying within the shape. This results in a start and end point.
        adjacency_matrix = np.zeros(shape=(n_elements,n_elements), dtype=np.float32)
        for element1_i, element1 in enumerate(elements):
            for element2_i, element2 in enumerate(elements):
                # Only adjacent if they share a border, not just a corner point
                if element1==element2:
                    pass
                    continue
                intersection = element1.intersection(element2)
                if intersection.is_empty:
                    continue 
                elif intersection.geom_type=='Point':
                    adjacency_matrix[element1_i, element2_i] = 1.5
                elif intersection.geom_type=='LineString':
                    adjacency_matrix[element1_i, element2_i] = 1
        return adjacency_matrix
    
    
    
# test_polygons = gpd.read_file('./test_polygons.geojson')
# poly = test_polygons.geometry[3]

# n_subpolygons = 3
# weights = [1/n_subpolygons] * n_subpolygons

# splitter = BlockSplitter(
#     polygon = poly,
#     subpolygon_weights = weights,
#     block_size = 0.1,
#     )
# splitter.prep_shape()
# splitter.optimize_polygon_split()
# MultiPolygon(splitter.final_shapes())
