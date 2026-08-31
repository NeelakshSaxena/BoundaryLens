import os
import requests
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from config.config_loader import get_active_config

def load_bare_earth_dem():
    config = get_active_config()
    print(f"Downloading Bare-Earth DEM (SRTM) for {config['region_name']}...")
    
    bbox = config["bbox"]
    lon_min, lat_min, lon_max, lat_max = bbox
    out_path = os.path.join("data", "raw", "bare_earth_dem.tif")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    # Use OpenTopography SRTM GL1 API
    url = f"https://portal.opentopography.org/API/globaldem?demtype=SRTMGL1&south={lat_min}&north={lat_max}&west={lon_min}&east={lon_max}&outputFormat=GTiff"
    
    try:
        print(f"Fetching SRTM 30m from OpenTopography...")
        r = requests.get(url, stream=True, timeout=30)
        
        if r.status_code == 200:
            with open(out_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Successfully downloaded Bare-Earth DEM to {out_path}")
            
            # Basic validation
            import rasterio
            with rasterio.open(out_path) as src:
                print(f"Validation: CRS={src.crs}, Resolution={src.res}, Bounds={src.bounds}")
        else:
            print(f"Failed to download. OpenTopography returned status code {r.status_code}")
            print("DEM STATUS: INVALID / UNSUPPORTED")
            print("STOP HEIGHT DERIVATION. Required DEM source could not be obtained.")
            
    except Exception as e:
        print(f"Failed to download DEM automatically: {e}")
        print("DEM STATUS: INVALID / UNSUPPORTED")
        print("STOP HEIGHT DERIVATION.")

if __name__ == "__main__":
    load_bare_earth_dem()
