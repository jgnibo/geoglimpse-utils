import geopandas as gpd
import numpy as np
from shapely.geometry import Polygon
import pyproj
from shapely.ops import transform

def create_hexagon(center_x, center_y, hex_size):
    """Create a hexagon based on center coordinates and size."""
    angle = np.arange(0, 2 * np.pi, 2 * np.pi / 6)
    hexagon_points = [(center_x + hex_size * np.cos(a), center_y + hex_size * np.sin(a)) for a in angle]
    hexagon_points.append(hexagon_points[0])
    return Polygon(hexagon_points)

def create_hex_grid(geojson_boundary, hex_size):
    large_area = gpd.read_file(geojson_boundary)

    utm_crs = pyproj.CRS.from_user_input(f"EPSG:32619")
    large_area_utm = large_area.to_crs(utm_crs)

    minx, miny, maxx, maxy = large_area_utm.total_bounds

    hex_height = np.sqrt(3) * hex_size
    hex_width = 2 * hex_size

    horiz_dist = hex_width * 0.75
    vert_dist = hex_height

    grid_cells = []
    row_num = 0
    x_min = minx
    y_min = miny - vert_dist  # Start slightly outside the area

    while y_min < maxy:
        x_offset = 0 if row_num % 2 == 0 else hex_width * 0.5 
        x = x_min + x_offset

        while x < maxx:
            hexagon = create_hexagon(x, y_min, hex_size)
            grid_cells.append(hexagon)
            x += horiz_dist

        y_min += vert_dist * 0.75 
        row_num += 1

    grid = gpd.GeoDataFrame({'geometry': grid_cells}, crs=utm_crs)

    clipped_grid = gpd.overlay(grid, large_area_utm, how='intersection')

    clipped_grid_wgs = clipped_grid.to_crs(large_area.crs)

    return clipped_grid_wgs

hex_size = 5.77  # Rough radius for a hexagon with area of 100m^2
tiles_geojson = create_hex_grid('./area.geojson', hex_size)

tiles_geojson.to_file("hex_grid_test.geojson", driver='GeoJSON')