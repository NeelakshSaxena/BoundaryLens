import os
import json
import numpy as np

def load_geojson(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    print("=========================================")
    print("  PHASE 6: CHENNAI ELEVATION EXTRACTION  ")
    print("=========================================\n")
    
    try:
        from shapely.geometry import shape
        import rasterio
        from rasterio.mask import mask
    except ImportError:
        print("Error: Required geospatial libraries missing.")
        return

    bldgs_path = os.path.join("data", "processed", "chennai_buildings_linked_2d.geojson")
    dem_path = os.path.join("data", "raw", "cartodem_chennai.tif")
    
    if not os.path.exists(bldgs_path) or not os.path.exists(dem_path):
        print(f"Error: Missing required files ({bldgs_path} or {dem_path}).")
        return

    bldgs_data = load_geojson(bldgs_path)
    total_bldgs = len(bldgs_data['features'])
    print(f"Loaded {total_bldgs} buildings. Processing ground elevation from CartoDEM...")

    extracted_count = 0

    with rasterio.open(dem_path) as dem_src:
        for b in bldgs_data["features"]:
            geom = shape(b["geometry"])
            
            try:
                # Mask bare earth CartoDEM for ground elevation reference
                dem_image, _ = mask(dem_src, [geom], crop=True, filled=True, all_touched=True)
                valid_dem = dem_image[(dem_image != dem_src.nodata) & (~np.isnan(dem_image))]
                
                if len(valid_dem) > 0:
                    b["properties"]["ground_elevation_m"] = round(float(np.median(valid_dem)), 2)
                    extracted_count += 1
                else:
                    b["properties"]["ground_elevation_m"] = 0.0 # Default if outside bounds
            except Exception as e:
                b["properties"]["ground_elevation_m"] = 0.0

    # Overwrite the file with the new elevation data
    with open(bldgs_path, "w", encoding="utf-8") as f:
        json.dump(bldgs_data, f, indent=2)

    print(f"\n3D Extraction complete. Valid Ground Elevations: {extracted_count}")

if __name__ == "__main__":
    main()
