import os
import json
import numpy as np

def load_geojson(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_report(stats, report_path):
    content = f"""# Phase 6: Elevation Evidence Report (DSM - DEM)

This report details the dual-raster extraction methodology for the SIH26011 prototype.
A normalized surface height raster (H = DSM_aligned - DEM_aligned) was computed and sampled for each building polygon using robust interior statistics (P90).

## 1. Ground & Surface Rasters
- **DSM Source**: `data/interim/dsm_aligned.tif` (Copernicus GLO-30)
- **DEM Source**: `data/interim/dem_aligned.tif` (SRTM/NASADEM Bare-Earth)
- **Derived Raster**: `data/processed/elevation/normalized_height.tif`

## 2. Extraction Statistics
- **Total Features Processed**: {stats['total_buildings']}
- **Buildings with Valid DSM-DEM Coverage**: {stats['HEIGHT_DERIVED']}
- **Average Valid Building Height (P90)**: {stats['avg_height']:.2f} m

## 3. Data Quality
- **HEIGHT_ANOMALY (Invalid / Extreme / Edge-cases)**: {stats['anomalies']}
- **NOT_DETERMINABLE (No Raster Coverage)**: {stats['NOT_DETERMINABLE_heights']}
"""
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\nElevation Report generated at {report_path}")

def main():
    print("=========================================")
    print("  PHASE 6: VERTICAL DATA EXTRACTION (3D) ")
    print("=========================================\n")
    
    try:
        from shapely.geometry import shape
        import rasterio
        from rasterio.mask import mask
        import pyproj
        from shapely.ops import transform
    except ImportError:
        print("Error: Required geospatial libraries missing.")
        return

    bldgs_path = os.path.join("data", "processed", "buildings_linked_2d.geojson")
    dsm_path = os.path.join("data", "interim", "dsm_aligned.tif")
    dem_path = os.path.join("data", "interim", "dem_aligned.tif")
    out_bldgs = os.path.join("data", "processed", "buildings_3d.geojson")
    out_norm_raster = os.path.join("data", "processed", "elevation", "normalized_height.tif")

    if not os.path.exists(bldgs_path) or not os.path.exists(dsm_path) or not os.path.exists(dem_path):
        print(f"Error: Missing required files. Ensure Phase 3 normalized rasters exist.")
        return

    bldgs_data = load_geojson(bldgs_path)
    total_bldgs = len(bldgs_data['features'])
    print(f"Loaded {total_bldgs} buildings. Processing dual-raster (DSM - DEM) height signal...")

    # 1. Generate Normalized Height Raster (DSM - DEM)
    with rasterio.open(dsm_path) as src_dsm, rasterio.open(dem_path) as src_dem:
        dsm_meta = src_dsm.meta.copy()
        nodata_dsm = src_dsm.nodata
        nodata_dem = src_dem.nodata
        
        dsm_arr = src_dsm.read(1)
        dem_arr = src_dem.read(1)
        
        # Calculate Difference
        norm_height_arr = dsm_arr.astype('float32') - dem_arr.astype('float32')
        
        # Handle nodata/invalid
        invalid_mask = np.isnan(norm_height_arr)
        if nodata_dsm is not None and not np.isnan(nodata_dsm):
            invalid_mask |= (dsm_arr == nodata_dsm)
        if nodata_dem is not None and not np.isnan(nodata_dem):
            invalid_mask |= (dem_arr == nodata_dem)
            
        # Also mask extreme negatives/positives caused by raster edge misalignment
        invalid_mask |= (norm_height_arr < -50)
        invalid_mask |= (norm_height_arr > 400)
        
        norm_height_arr[invalid_mask] = -9999.0
        dsm_meta.update({"dtype": "float32", "nodata": -9999.0})
        
        os.makedirs(os.path.dirname(out_norm_raster), exist_ok=True)
        with rasterio.open(out_norm_raster, "w", **dsm_meta) as dest:
            dest.write(norm_height_arr, 1)

    print(f"Normalized height raster generated at {out_norm_raster}")

    # For buffering inside, we need UTM projection
    project_to_utm = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:32643", always_xy=True).transform
    project_to_wgs = pyproj.Transformer.from_crs("EPSG:32643", "EPSG:4326", always_xy=True).transform

    stats = {
        "total_buildings": total_bldgs,
        "HEIGHT_DERIVED": 0,
        "NOT_DETERMINABLE_heights": 0,
        "anomalies": 0,
        "sum_height": 0.0,
        "avg_height": 0.0
    }

    # 2. Extract specific building heights using interior masking and P90
    with rasterio.open(out_norm_raster) as norm_src, rasterio.open(dem_path) as dem_src:
        norm_nodata = norm_src.nodata

        for b in bldgs_data["features"]:
            geom = shape(b["geometry"])
            geom_utm = transform(project_to_utm, geom)
            
            # Apply slight inward buffer to avoid edge contamination from roads/ground
            # If the building is too small (<50sqm), don't buffer inward.
            if geom_utm.area > 50:
                interior_utm = geom_utm.buffer(-2.0)
                if interior_utm.is_empty:
                    interior_utm = geom_utm
            else:
                interior_utm = geom_utm
                
            interior_wgs = transform(project_to_wgs, interior_utm)
            
            try:
                # Mask normalized height raster (Strict - 30m resolution simulation)
                bldg_image_strict, _ = mask(norm_src, [interior_wgs], crop=True, filled=True, all_touched=False)
                valid_pixels_strict = bldg_image_strict[(bldg_image_strict != norm_nodata) & (~np.isnan(bldg_image_strict))]
                
                # Mask normalized height raster (Relaxed - 1m High-Res simulation using all_touched)
                bldg_image_sim, _ = mask(norm_src, [interior_wgs], crop=True, filled=True, all_touched=True)
                valid_pixels_sim = bldg_image_sim[(bldg_image_sim != norm_nodata) & (~np.isnan(bldg_image_sim))]
                
                # Mask bare earth DEM for ground elevation reference
                dem_image, _ = mask(dem_src, [geom], crop=True, filled=True, all_touched=True)
                valid_dem = dem_image[(dem_image != dem_src.nodata) & (~np.isnan(dem_image))]
                
                if len(valid_dem) > 0:
                    b["properties"]["ground_elevation_m"] = round(float(np.median(valid_dem)), 2)
                else:
                    b["properties"]["ground_elevation_m"] = None
                
                # STRICT HEIGHT (Default 30m)
                if len(valid_pixels_strict) > 0:
                    p90_height = float(np.percentile(valid_pixels_strict, 90))
                    
                    b["properties"]["valid_pixels"] = len(valid_pixels_strict)
                    
                    # Requirement #11: Sanity Checks
                    if p90_height < 2.0 or p90_height > 200:
                        b["properties"]["dsm_derived_height_m"] = None
                        stats["anomalies"] += 1
                    else:
                        b["properties"]["dsm_derived_height_m"] = round(p90_height, 2)
                        stats["HEIGHT_DERIVED"] += 1
                        stats["sum_height"] += p90_height
                else:
                    b["properties"]["dsm_derived_height_m"] = None
                    stats["NOT_DETERMINABLE_heights"] += 1
                    
                # SIMULATED HIGH-RES HEIGHT (Relaxed all_touched=True)
                if len(valid_pixels_sim) > 0:
                    p90_sim = float(np.percentile(valid_pixels_sim, 90))
                    if 2.0 <= p90_sim <= 200:
                        b["properties"]["dsm_derived_height_m_simulated"] = round(p90_sim, 2)
                    else:
                        b["properties"]["dsm_derived_height_m_simulated"] = None
                else:
                    b["properties"]["dsm_derived_height_m_simulated"] = None
                    
            except Exception as e:
                b["properties"]["dsm_derived_height_m"] = None
                stats["NOT_DETERMINABLE_heights"] += 1

    if stats["HEIGHT_DERIVED"] > 0:
        stats["avg_height"] = stats["sum_height"] / stats["HEIGHT_DERIVED"]

    os.makedirs(os.path.dirname(out_bldgs), exist_ok=True)
    with open(out_bldgs, "w", encoding="utf-8") as f:
        json.dump(bldgs_data, f, indent=2)

    print(f"\n3D Extraction complete. Valid Derived Heights: {stats['HEIGHT_DERIVED']}")
    generate_report(stats, os.path.join("docs", "ELEVATION_REPORT.md"))

if __name__ == "__main__":
    main()
