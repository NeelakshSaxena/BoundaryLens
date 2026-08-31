import subprocess
import sys
import time

def run_script(script_path):
    print(f"\n[{time.strftime('%H:%M:%S')}] Executing: {script_path}")
    print("-" * 50)
    result = subprocess.run([sys.executable, script_path], check=False)
    if result.returncode != 0:
        print(f"\n[ERROR] Script {script_path} failed with exit code {result.returncode}")
        print("Pipeline aborted.")
        sys.exit(result.returncode)

def main():
    print("==================================================")
    print(" BoundaryLens SIH26011 - Full Pipeline Execution  ")
    print("==================================================\n")

    scripts = [
        # Initialization & Ingestion
        "scripts/01_select_aoi.py",
        "scripts/ingestion/load_osm.py",
        "scripts/ingestion/load_cadastral.py",
        "scripts/ingestion/load_copernicus_dem.py",
        "scripts/ingestion/load_bare_earth_dem.py",
        
        # Processing & Normalisation
        "scripts/03_normalise_layers.py",
        "scripts/04_validate_data_quality.py",
        
        # Spatial Matching & Topology
        "scripts/05_match_parcels_buildings.py",
        
        # 3D Extraction & Real Data Evidence
        "scripts/06_extract_elevation.py",
        "scripts/08_fetch_real_heights.py",
        "scripts/08_extract_floor_entities.py",
        
        # AI & Fusion Engine
        "scripts/09_detect_anomalies_ai.py",
        "scripts/10_fuse_evidence_engine.py",
        
        # Master Outputs & Compliance
        # Note: 14_generate_vertical_ulpins.py was removed to strictly adhere to "No Fake ULPIN" rule.
    ]

    for script in scripts:
        run_script(script)

    print("\n==================================================")
    print(" PIPELINE COMPLETE! STARTING WEB UI ")
    print("==================================================")
    
    print("\nStarting MapLibre 3D UI on http://localhost:8000")
    print("Press Ctrl+C to stop the server.\n")
    
    try:
        subprocess.run([sys.executable, "-m", "http.server", "8000", "--directory", "frontend"])
    except KeyboardInterrupt:
        print("\nServer stopped. Pipeline execution finished.")

if __name__ == "__main__":
    main()
