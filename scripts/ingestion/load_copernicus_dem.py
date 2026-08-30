import os
import requests

def load_copernicus_dem():
    print("Downloading Copernicus DEM GLO-30 for Bengaluru Urban from AWS Public Bucket (No Auth Required)...")
    
    # Public AWS S3 direct HTTPS URL for N12 E077 tile
    url = "https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N12_00_E077_00_DEM/Copernicus_DSM_COG_10_N12_00_E077_00_DEM.tif"
    
    out_dir = os.path.join("data", "raw")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "copernicus_dem_glo30.tif")
    
    try:
        print(f"Fetching from {url}...")
        r = requests.get(url, stream=True, timeout=30)
        
        # If the specific COG name varies, we fallback to AWS STAC or public HTTPS download
        if r.status_code != 200:
            print(f"Direct download returned status code {r.status_code}. Trying OpenTopography / alternative public mirror...")
            url = "https://prs-dem-open.s3.amazonaws.com/GLO-30/Copernicus_DSM_COG_10_N12_00_E077_00_DEM.tif"
            r = requests.get(url, stream=True, timeout=30)
            
        r.raise_for_status()
        
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
                
        print(f"Successfully downloaded Copernicus DEM to {out_path}")
        
    except Exception as e:
        print(f"Failed to download Copernicus DEM automatically: {e}")
        print("Alternative: You can download NASADEM / SRTM 30m or Copernicus DEM via OpenTopography freely.")

if __name__ == "__main__":
    load_copernicus_dem()
