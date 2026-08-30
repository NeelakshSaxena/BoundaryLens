import os
import requests

def load_cadastral():
    print("Loading Bengaluru Cadastral Maps from OpenCity...")
    
    # URL obtained from Phase 1 Audit
    url = "https://data.opencity.in/dataset/b5d91825-a104-41c8-bf93-3aedcfd58124/resource/3975e8d0-9a23-4b4b-a3c9-9453979406e4/download/038b4a89-98c8-49f7-aa1a-b3d073745d0b.kmz"
    
    try:
        r = requests.get(url, stream=True)
        r.raise_for_status()
        
        out_dir = os.path.join("data", "raw")
        os.makedirs(out_dir, exist_ok=True)
        
        out_path = os.path.join(out_dir, "bengaluru_cadastral.kmz")
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
                
        print(f"Successfully saved Cadastral KMZ to {out_path}")
        
    except Exception as e:
        print(f"Failed to download Cadastral data: {e}")

if __name__ == "__main__":
    load_cadastral()
