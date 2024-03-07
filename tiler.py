import geopandas as gpd
from shapely.geometry import box
import numpy as np
import math

def create_grid(geojson_boundary, tile_size_meters):
    large_area = gpd.read_file(geojson_boundary)

    if large_area.crs is None:
        large_area.crs = "EPSG:4326"

    minx, miny, maxx, maxy = large_area.total_bounds

    # These are for converting latitutde and longitude to meters. Longitude requires some extra math that I found somewhere online
    lat_step = tile_size_meters / 111000  
    lon_step = tile_size_meters / (111000 * math.cos(math.radians((miny + maxy) / 2)))

    grid_cells = []
    for x in np.arange(minx, maxx, lon_step):
        for y in np.arange(miny, maxy, lat_step):
            grid_cells.append(box(x, y, x + lon_step, y + lat_step))

    grid = gpd.GeoDataFrame(grid_cells, columns=['geometry'], crs=large_area.crs)

    clipped_grid = gpd.overlay(grid, large_area, how='intersection')

    return clipped_grid

tiles_geojson = create_grid('./area.geojson', 10)

tiles_geojson.to_file("tiled_grid.geojson", driver='GeoJSON')