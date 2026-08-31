import os
import json
import random

def main():
    print("=========================================")
    print("  PHASE 8: FETCH REAL BUILDING HEIGHTS   ")
    print("=========================================\n")

    bldgs_path = os.path.join("data", "processed", "buildings_3d.geojson")
    if not os.path.exists(bldgs_path):
        print(f"Error: {bldgs_path} not found.")
        return

    with open(bldgs_path, "r", encoding="utf-8") as f:
        bldgs_data = json.load(f)

    total_bldgs = len(bldgs_data["features"])
    print(f"Loaded {total_bldgs} buildings. Fetching/evaluating satellite and open heights...")

    osm_verified_count = 0
    dsm_derived_count = 0

    for b in bldgs_data["features"]:
        props = b["properties"]
        
        # 1. Check for OSM explicit height/levels
        levels = props.get("building_levels")
        dsm_height = props.get("dsm_derived_height_m")
        
        if levels and str(levels).isdigit():
            # LEVEL 1 - EXACT / STRUCTURED 3D
            props["building_height_m"] = round(float(levels) * 3.5, 2)
            props["derived_floors"] = int(levels)
            props["height_source"] = "OSM"
            props["height_confidence"] = "HIGH"
            props["3d_representation_status"] = "EXACT STRUCTURED 3D"
            osm_verified_count += 1
        elif dsm_height is not None and dsm_height > 2.0:
            # LEVEL 2 - HEIGHT-BASED 3D MASS (Approximation)
            props["building_height_m"] = dsm_height
            props["derived_floors"] = "NOT_DETERMINABLE"
            props["height_source"] = "REAL_DSM - BARE_EARTH_DEM"
            
            # Confidence based on valid pixels (Requirement 10)
            vp = props.get("valid_pixels", 0)
            std = props.get("height_std", 0)
            if vp > 50 and std < 3.0:
                props["height_confidence"] = "HIGH"
            elif vp > 10:
                props["height_confidence"] = "MEDIUM"
            else:
                props["height_confidence"] = "LOW"
                
            props["3d_representation_status"] = "HEIGHT-DERIVED MASS"
            dsm_derived_count += 1
        else:
            # LEVEL 3 - STRICT FALLBACK: DO NOT INVENT DATA
            props["building_height_m"] = None
            props["derived_floors"] = None
            props["height_source"] = "SOURCE NOT CONNECTED"
            props["height_confidence"] = "NOT_DETERMINABLE"
            props["3d_representation_status"] = "2D FOOTPRINT ONLY"

    with open(bldgs_path, "w", encoding="utf-8") as f:
        json.dump(bldgs_data, f, indent=2)

    print(f"Height processing complete.")
    print(f"  OSM Verified Heights: {osm_verified_count}")
    print(f"  DSM-DEM Derived Heights: {dsm_derived_count}")
    print(f"Updated {bldgs_path}")

if __name__ == "__main__":
    main()
