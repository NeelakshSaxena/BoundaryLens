# Phase 8: Floor Evidence Extraction Report

This report documents the extraction of 3D multi-storey floor entities linking physical structures to cadastral parcels in Bengaluru Urban.

## 1. Summary Statistics
- **Total Buildings Analyzed**: 2734
- **Total Discrete Floor Entities Extracted**: 577173
- **Average Floors per Building**: 211.11

## 2. Floor Count Distribution
| Floor Count | Building Count | Percentage |
| :--- | :--- | :--- |
| **1 Floors** (3.5m) | 1 | 0.0% |
| **2 Floors** (7.0m) | 29 | 1.1% |
| **3 Floors** (10.5m) | 51 | 1.9% |
| **4 Floors** (14.0m) | 84 | 3.1% |
| **5 Floors** (17.5m) | 2 | 0.1% |
| **11 Floors** (38.5m) | 3 | 0.1% |
| **114 Floors** (399.0m) | 8 | 0.3% |
| **115 Floors** (402.5m) | 87 | 3.2% |
| **116 Floors** (406.0m) | 46 | 1.7% |
| **117 Floors** (409.5m) | 11 | 0.4% |
| **229 Floors** (801.5m) | 21 | 0.8% |
| **230 Floors** (805.0m) | 402 | 14.7% |
| **231 Floors** (808.5m) | 683 | 25.0% |
| **232 Floors** (812.0m) | 636 | 23.3% |
| **233 Floors** (815.5m) | 414 | 15.1% |
| **234 Floors** (819.0m) | 200 | 7.3% |
| **235 Floors** (822.5m) | 36 | 1.3% |
| **236 Floors** (826.0m) | 15 | 0.5% |
| **237 Floors** (829.5m) | 4 | 0.1% |
| **238 Floors** (833.0m) | 1 | 0.0% |

## 3. Data Provenance & Evidence Hierarchy (Rule 3)
| Source | Count | Confidence | Provenance Description |
| :--- | :--- | :--- | :--- |
| `REAL_DSM - BARE_EARTH_DEM` | 2564 | `MEDIUM` | DEM-derived height or simulated approximation |
| `ESTIMATED_FOOTPRINT_AREA` | 154 | `MEDIUM` | DEM-derived height or simulated approximation |
| `OSM` | 16 | `MEDIUM` | DEM-derived height or simulated approximation |

**Output Artefacts**:
- Floor Entities Database: `data/processed/floor_entities.json`
- Updated 3D Web UI Dataset: `frontend/data/buildings_3d.geojson`
