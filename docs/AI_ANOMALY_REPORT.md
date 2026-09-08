# Phase 9: AI Anomaly Detection Report (Isolation Forest)

This report details the unsupervised Machine Learning analysis conducted on the 2,734 3D building entities in Bengaluru Urban, strictly following **Project Rule 5** (*AI assists; it does not adjudicate legal rights*).

## 1. Model Configuration
- **Algorithm**: `sklearn.ensemble.IsolationForest`
- **Contamination Parameter**: `0.03` (Top 3% spatial/vertical outliers)
- **Feature Matrix Inputs**:
  1. `parcel_overlap_ratio` (2D Spatial Boundary Intersection)
  2. `building_height_m` (Satellite Height)
  3. `ground_elevation_m` (Copernicus DEM Terrain)
  4. `derived_floors` (Multi-Storey Count)

## 2. Detection Results
- **Total Buildings Evaluated**: 2734
- **Normal Inliers**: 2652
- **AI Anomaly Flags Raised**: 82 (3.00%)

## 3. Sample Flagged Spatial/Vertical Conflicts
| Building ID | Linked Parcel | 2D Match Status | Height | Overlap | AI Anomaly Score |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `osm_way_345860231` | `cadastral_parcel_22433` | `MAJORITY` | 10.5m | 0.5138 | `-0.0773` |
| `osm_way_345862795` | `cadastral_parcel_22457` | `MAJORITY` | 407.0m | 0.5871 | `-0.0469` |
| `osm_way_347151275` | `cadastral_parcel_22074` | `MAJORITY` | 409.5m | 0.9179 | `-0.0263` |
| `osm_way_347151666` | `cadastral_parcel_22060` | `MAJORITY` | 407.5m | 0.8019 | `-0.018` |
| `osm_way_347151672` | `cadastral_parcel_22254` | `CONTAINED` | 7.0m | 0.9914 | `-0.0242` |
| `osm_way_347152009` | `cadastral_parcel_22060` | `MAJORITY` | 407.5m | 0.8866 | `-0.0012` |
| `osm_way_347152552` | `cadastral_parcel_22254` | `CONTAINED` | 7.0m | 1.0 | `-0.0139` |
| `osm_way_347153086` | `cadastral_parcel_22079` | `MAJORITY` | 407.5m | 0.7475 | `-0.0243` |
| `osm_way_347153308` | `cadastral_parcel_22254` | `CONTAINED` | 7.0m | 1.0 | `-0.0139` |
| `osm_way_347159054` | `cadastral_parcel_22454` | `CONTAINED` | 7.0m | 1.0 | `-0.0139` |

**Output File**: `data/processed/buildings_ai_analyzed.geojson`
