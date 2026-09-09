import os
import requests
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from config.config_loader import get_active_config

def load_bare_earth_dem():
    config = get_active_config()
    print(f"Downloading Bare-Earth DEM (SRTM) for {config['region_name']}...")
    
    bbox = config["bbox"]
    lon_min, lat_min, lon_max, lat_max = bbox
    out_path = os.path.join("data", "raw", "bare_earth_dem.tif")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    if os.path.exists(out_path):
        print(f"File {out_path} already exists. Skipping download.")
        return
    
    # Use OpenTopography SRTM GL1 API
    api_key = os.environ.get("OPEN_TOPOGRAPHY_API", "")
    url = f"https://portal.opentopography.org/API/globaldem?demtype=SRTMGL1&south={lat_min}&north={lat_max}&west={lon_min}&east={lon_max}&outputFormat=GTiff"
    if api_key:
        url += f"&API_Key={api_key}"
    
    try:
        print(f"Fetching SRTM 30m from OpenTopography...")
        r = requests.get(url, stream=True, timeout=30)
        
        if r.status_code == 200:
            with open(out_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Successfully downloaded Bare-Earth DEM to {out_path}")
            
            # Basic validation
            try:
                import rasterio
                with rasterio.open(out_path) as src:
                    print(f"Validation: CRS={src.crs}, Resolution={src.res}, Bounds={src.bounds}")
            except ImportError:
                print("rasterio not installed, skipping validation.")
        else:
            print(f"Failed to download. OpenTopography returned status code {r.status_code}")
            print(f"Response text: {r.text}")
            print("DEM STATUS: INVALID / UNSUPPORTED")
            print("STOP HEIGHT DERIVATION. Required DEM source could not be obtained.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Failed to download DEM automatically: {e}")
        print("DEM STATUS: INVALID / UNSUPPORTED")
        print("STOP HEIGHT DERIVATION.")
        sys.exit(1)

if __name__ == "__main__":
    load_bare_earth_dem()
