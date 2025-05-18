import json
import pandas as pd
from geopy.distance import geodesic

def extract_poi_coordinate(geojson_path, csv_path, target_link_id):
    import json
    import pandas as pd
    from geopy.distance import geodesic

    target_link_id_str = str(target_link_id)

    # Load GeoJSON
    with open(geojson_path, 'r') as f:
        geojson = json.load(f)

    # Find the feature with matching link_id (cast to str for matching)
    feature = next(
        (f for f in geojson['features']
         if str(f['properties'].get('link_id')) == target_link_id_str),
        None
    )

    if not feature:
        raise ValueError(f"Link ID {target_link_id} not found in GeoJSON")

    coordinates = feature['geometry']['coordinates']

    # Validate coordinates
    if not coordinates or not all(isinstance(coord, list) and len(coord) == 2 for coord in coordinates):
        raise ValueError(f"Invalid or missing coordinates for link_id {target_link_id}")

    # Reference node = lowest latitude then longitude
    ref_node = min(coordinates, key=lambda x: (x[1], x[0]))

    # Load CSV and find matching row
    df = pd.read_csv(csv_path)
    df['LINK_ID'] = df['LINK_ID'].astype(str)

    row = df[df['LINK_ID'] == target_link_id_str]
    if row.empty:
        raise ValueError(f"Link ID {target_link_id} not found in CSV")

    percfrref = float(row.iloc[0]['PERCFRREF'])

    # Path length function
    def path_length(coords):
        return sum(
            geodesic(coords[i][::-1], coords[i+1][::-1]).meters
            for i in range(len(coords) - 1)
        )

    total_length = path_length(coordinates)
    target_distance = total_length * (percfrref / 100.0)

    # Interpolate
    def interpolate_point(coords, target_m):
        traversed = 0.0
        for i in range(len(coords) - 1):
            start, end = coords[i], coords[i + 1]
            seg_len = geodesic(start[::-1], end[::-1]).meters

            if traversed + seg_len >= target_m:
                ratio = (target_m - traversed) / seg_len
                lon = start[0] + ratio * (end[0] - start[0])
                lat = start[1] + ratio * (end[1] - start[1])
                return [lon, lat]
            traversed += seg_len

        return coords[-1]  # fallback

    poi_coord = interpolate_point(coordinates, target_distance)

    return {
        'reference_node': ref_node,
        'percfrref': percfrref,
        'poi_coordinate': poi_coord
    }
