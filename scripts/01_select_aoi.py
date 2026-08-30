import json
import os

# Jayanagar / Koramangala area is dense. 
# Center approx: 12.9300° N, 77.6200° E
# 2 sq km is roughly 1.414 km x 1.414 km.
# 1 degree lat is ~111km. 1.414km is ~0.0127 degrees.
# Delta lat/lon from center = 0.0127 / 2 = 0.00635 degrees.

CENTER_LAT = 12.9300
CENTER_LON = 77.6200
OFFSET = 0.00635

lat_min = CENTER_LAT - OFFSET
lat_max = CENTER_LAT + OFFSET
lon_min = CENTER_LON - OFFSET
lon_max = CENTER_LON + OFFSET

bbox_geojson = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "name": "Bengaluru Urban 2sqkm AOI"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [lon_min, lat_min],
                    [lon_max, lat_min],
                    [lon_max, lat_max],
                    [lon_min, lat_max],
                    [lon_min, lat_min]
                ]]
            }
        }
    ]
}

def main():
    out_dir = os.path.join("data", "raw")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "aoi_bbox.geojson")
    with open(out_path, "w") as f:
        json.dump(bbox_geojson, f, indent=2)
    
    print(f"Generated 2 sq km AOI bounding box at {out_path}")
    print(f"BBox (South, North, West, East): {lat_min}, {lat_max}, {lon_min}, {lon_max}")

if __name__ == "__main__":
    main()
