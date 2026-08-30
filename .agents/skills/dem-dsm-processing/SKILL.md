# DEM/DSM Processing Skill

DEM = ground/terrain elevation.
DSM = surface elevation.

Align compatible rasters before calculating DSM-DEM.

Check:
- CRS
- resolution
- bounds
- nodata
- vertical reference
- plausible value range

Never claim that DSM alone gives exact floor count.

Stop if DEM/DSM semantics or vertical reference cannot be established.
