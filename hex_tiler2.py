import geopandas as gpd
import h3pandas

#one-liner
hex_area = gpd.read_file('./area.geojson').h3.polyfill_resample(12).h3.h3_to_geo_boundary().to_file("hex_grid_test.geojson", driver='GeoJSON')
