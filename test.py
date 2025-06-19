import geopandas as gpd
zones = gpd.read_file("data/zones.geojson")
print(zones.columns)
