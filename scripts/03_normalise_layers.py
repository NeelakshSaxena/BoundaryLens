import os
import json
import zipfile
import xml.etree.ElementTree as ET

# Target AOI BBox coordinates from 01_select_aoi.py
LAT_MIN, LAT_MAX = 12.92365, 12.93635
LON_MIN, LON_MAX = 77.61365, 77.62635

def is_point_in_aoi(lon, lat):
    return LON_MIN <= lon <= LON_MAX and LAT_MIN <= lat <= LAT_MAX

def is_polygon_in_aoi(coords):
    # coords is list of [lon, lat]
    for lon, lat in coords:
        if is_point_in_aoi(lon, lat):
            return True
    return False

def normalise_osm():
    print("--- 1. Normalising OSM Building Footprints & Levels ---")
    raw_path = os.path.join("data", "raw", "osm_data.json")
    out_path = os.path.join("data", "interim", "osm_buildings_normalised.geojson")
    
    if not os.path.exists(raw_path):
        print(f"Error: Raw file {raw_path} not found.")
        return

    with open(raw_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Index nodes by ID
    nodes = {}
    elements = data.get("elements", [])
    for elem in elements:
        if elem.get("type") == "node":
            nodes[elem["id"]] = [elem["lon"], elem["lat"]]

    features = []
    building_count = 0
    levels_count = 0

    for elem in elements:
        if elem.get("type") == "way" and "tags" in elem:
            tags = elem["tags"]
            if "building" in tags:
                way_nodes = elem.get("nodes", [])
                coords = [nodes[node_id] for node_id in way_nodes if node_id in nodes]
                
                if len(coords) >= 3 and is_polygon_in_aoi(coords):
                    # Ensure polygon ring is closed
                    if coords[0] != coords[-1]:
                        coords.append(coords[0])
                    
                    levels = tags.get("building:levels")
                    height = tags.get("height")
                    
                    try:
                        levels_num = float(levels) if levels else None
                    except ValueError:
                        levels_num = None
                        
                    try:
                        height_num = float(height.replace("m", "").strip()) if height else None
                    except (ValueError, AttributeError):
                        height_num = None

                    if levels_num is not None:
                        levels_count += 1

                    feature = {
                        "type": "Feature",
                        "properties": {
                            "id": f"osm_way_{elem['id']}",
                            "source": "OpenStreetMap",
                            "building_type": tags.get("building", "yes"),
                            "name": tags.get("name"),
                            "building_levels": levels_num,
                            "height_m": height_num,
                            "crs": "EPSG:4326"
                        },
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [coords]
                        }
                    }
                    features.append(feature)
                    building_count += 1

    geojson_output = {
        "type": "FeatureCollection",
        "crs": {
            "type": "name",
            "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}
        },
        "features": features
    }

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(geojson_output, f, indent=2)

    print(f"Normalised {building_count} building footprints inside AOI.")
    print(f"Buildings with explicit 'building:levels' tag: {levels_count}")
    print(f"Saved to {out_path}\n")

def normalise_cadastral():
    print("--- 2. Normalising OpenCity Cadastral Parcels ---")
    raw_path = os.path.join("data", "raw", "bengaluru_cadastral.kmz")
    out_path = os.path.join("data", "interim", "cadastral_parcels_normalised.geojson")

    if not os.path.exists(raw_path):
        print(f"Error: Raw file {raw_path} not found.")
        return

    features = []
    parcel_count = 0

    try:
        with zipfile.ZipFile(raw_path, "r") as kmz:
            kml_files = [f for f in kmz.namelist() if f.endswith(".kml")]
            if not kml_files:
                print("No KML file found inside KMZ archive.")
                return
            
            kml_content = kmz.read(kml_files[0])
            root = ET.fromstring(kml_content)
            
            # Namespace handling for KML
            ns = {"kml": "http://www.opengis.net/kml/2.2"}

            for idx, placemark in enumerate(root.findall(".//kml:Placemark", ns)):
                name_elem = placemark.find("kml:name", ns)
                name = name_elem.text if name_elem is not None else f"parcel_{idx}"

                # Extract coordinates from Polygon outerBoundaryIs
                coord_elem = placemark.find(".//kml:outerBoundaryIs/kml:LinearRing/kml:coordinates", ns)
                if coord_elem is None:
                    # Fallback search without namespace prefix if necessary
                    coord_elem = placemark.find(".//coordinates")

                if coord_elem is not None and coord_elem.text:
                    coord_str = coord_elem.text.strip()
                    raw_coords = coord_str.split()
                    coords = []
                    for pt in raw_coords:
                        parts = pt.split(",")
                        if len(parts) >= 2:
                            try:
                                lon, lat = float(parts[0]), float(parts[1])
                                coords.append([lon, lat])
                            except ValueError:
                                continue
                    
                    if len(coords) >= 3 and is_polygon_in_aoi(coords):
                        if coords[0] != coords[-1]:
                            coords.append(coords[0])
                            
                        feature = {
                            "type": "Feature",
                            "properties": {
                                "id": f"cadastral_parcel_{idx}",
                                "name": name,
                                "source": "OpenCity / BDA / KSRSAC",
                                "crs": "EPSG:4326"
                            },
                            "geometry": {
                                "type": "Polygon",
                                "coordinates": [coords]
                            }
                        }
                        features.append(feature)
                        parcel_count += 1

    except Exception as e:
        print(f"Failed to parse KMZ/KML: {e}")

    geojson_output = {
        "type": "FeatureCollection",
        "crs": {
            "type": "name",
            "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}
        },
        "features": features
    }

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(geojson_output, f, indent=2)

    print(f"Normalised & clipped {parcel_count} cadastral parcels inside AOI.")
    print(f"Saved to {out_path}\n")

def normalise_dem():
    print("--- 3. Normalising DEM Raster ---")
    raw_path = os.path.join("data", "raw", "copernicus_dem_glo30.tif")
    out_path = os.path.join("data", "interim", "dem_normalised.tif")
    
    if not os.path.exists(raw_path):
        print(f"Error: Raw DEM {raw_path} not found.")
        return

    try:
        import rasterio
        from rasterio.mask import mask
        from shapely.geometry import box
        
        aoi_polygon = [box(LON_MIN, LAT_MIN, LON_MAX, LAT_MAX)]
        
        with rasterio.open(raw_path) as src:
            out_image, out_transform = mask(src, aoi_polygon, crop=True)
            out_meta = src.meta.copy()
            
            out_meta.update({
                "driver": "GTiff",
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform,
                "crs": "EPSG:4326"
            })
            
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with open(out_path, "wb") as f:
                with rasterio.open(out_path, "w", **out_meta) as dest:
                    dest.write(out_image)
                    
        print(f"Cropped DEM raster to AOI BBox and saved to {out_path}\n")
    except ImportError:
        print("rasterio package not installed. Creating normalized DEM file reference.")
        import shutil
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        shutil.copyfile(raw_path, out_path)
        print(f"Saved DEM reference to {out_path}\n")

def main():
    print("=========================================")
    print("  PHASE 3: LAYER NORMALISATION PIPELINE  ")
    print("=========================================\n")
    normalise_osm()
    normalise_cadastral()
    normalise_dem()
    print("Phase 3 Normalisation complete!")

if __name__ == "__main__":
    main()
