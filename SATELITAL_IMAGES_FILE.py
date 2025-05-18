import requests
import math
import geopandas as gpd
import os
import pandas as pd
from geo_utils import extract_poi_coordinate 

# Funciones previas (sin cambios)
def lat_lon_to_tile(lat, lon, zoom):
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    n = 2.0 ** zoom
    x = int((lon_rad - (-math.pi)) / (2 * math.pi) * n)
    y = int((1 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2 * n)
    return (x, y)

def tile_coords_to_lat_lon(x, y, zoom):
    n = 2.0 ** zoom
    lon_deg = x / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lon_deg)

def get_tile_bounds(x, y, zoom):
    lat1, lon1 = tile_coords_to_lat_lon(x, y, zoom)
    lat2, lon2 = tile_coords_to_lat_lon(x + 1, y, zoom)
    lat3, lon3 = tile_coords_to_lat_lon(x + 1, y + 1, zoom)
    lat4, lon4 = tile_coords_to_lat_lon(x, y + 1, zoom)
    return (lat1, lon1), (lat2, lon2), (lat3, lon3), (lat4, lon4)

def create_wkt_polygon(bounds):
    (lat1, lon1), (lat2, lon2), (lat3, lon3), (lat4, lon4) = bounds
    return f"POLYGON(({lon1} {lat1}, {lon2} {lat2}, {lon3} {lat3}, {lon4} {lat4}, {lon1} {lat1}))"

def get_satellite_tile(lat, lon, zoom, tile_format, api_key, output_path):
    x, y = lat_lon_to_tile(lat, lon, zoom)
    url = f"https://maps.hereapi.com/v3/base/mc/{zoom}/{x}/{y}/{tile_format}?style=satellite.day&size=512&apiKey={api_key}"

    response = requests.get(url)
    if response.status_code == 200:
        with open(output_path, 'wb') as file:
            file.write(response.content)
        print(f'Tile saved: {output_path}')
    else:
        print(f'Failed to retrieve tile ({lat}, {lon}) - Status code: {response.status_code}')

# CONFIGURACIÓN
GEOJSON_FOLDER = './STREETS_NAV/' #HERE YOU NEED THE GEOJSON DATASETS
CSV_FOLDER = './POIs/'           #HERE YOU NEED THE GEOJSON DATASETS
SATELLITE_FOLDER = 'satellite_tiles'
api_key = '' #API KEY GOES HERE
zoom = 18
tile_format = 'png'

os.makedirs(SATELLITE_FOLDER, exist_ok=True)

specific_geojson_file = 'SREETS_NAV_4815075.geojson' #INPUT YOUR GEOJSON FILE HERE
geojson_file_path = os.path.join(GEOJSON_FOLDER, specific_geojson_file)

# Cargar GeoDataFrame
streets_gdf = gpd.read_file(geojson_file_path).to_crs(epsg=4326)

if 'link_id' in streets_gdf.columns:
    streets_gdf.rename(columns={'link_id': 'LINK_ID'}, inplace=True)

# Cargar todos los CSV de POIs
csv_files = [f for f in os.listdir(CSV_FOLDER) if f.endswith(".csv")]
pois_df_list = []
for f in csv_files:
    df = pd.read_csv(os.path.join(CSV_FOLDER, f), low_memory=False)
    df.columns = [col.upper() for col in df.columns]
    pois_df_list.append(df)

pois_df = pd.concat(pois_df_list, ignore_index=True)

# Cast to string for reliable comparison
streets_gdf['LINK_ID'] = streets_gdf['LINK_ID'].astype(str)
pois_df['LINK_ID'] = pois_df['LINK_ID'].astype(str)

link_ids_pois = set(pois_df['LINK_ID'].unique())
filtered_streets = streets_gdf[streets_gdf['LINK_ID'].isin(link_ids_pois)]

max_images = 100
count = 0

# Solo usamos el primer archivo CSV para obtener PERCFRREF
# (Puedes adaptarlo para usar todos si es necesario)
poi_csv_path = os.path.join(CSV_FOLDER, csv_files[0])

for idx, row in filtered_streets.iterrows():
    if count >= max_images:
        break

    link_id = row['LINK_ID']
    try:
        result = extract_poi_coordinate(geojson_file_path, poi_csv_path, link_id)
        lat, lon = result['poi_coordinate'][1], result['poi_coordinate'][0]

        output_filename = os.path.join(SATELLITE_FOLDER, f"{link_id}.{tile_format}")
        get_satellite_tile(lat, lon, zoom, tile_format, api_key, output_filename)
        count += 1

    except Exception as e:
        print(f"Error processing LINK_ID {link_id}: {e}")
        continue
