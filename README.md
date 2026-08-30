# BoundaryLens Agentic Starter

This package contains the project constitution, phase plan, agent prompts and reusable skills for SIH26011.

Start here:
1. Read `AGENTS.md`.
2. Read `docs/TECH_AND_DATA_STRATEGY.md`.
3. Read `docs/PHASES.md`.
4. Run Phase 1 dataset discovery before writing ML code.
5. Use only one pilot AOI initially: Baramati ULB, Pune district, Maharashtra.
6. Treat DSM/LiDAR as optional Tier B until actually obtained and verified.

## Important
The public Bhuvan catalogue provides CartoDEM/DEM products. Do not present them as a city-scale DSM.
OpenStreetMap `building:levels` is useful evidence when present, but it is not a government cadastral record.
Microsoft/Google building footprints are physical mapping evidence, not proof of legal ownership.

The prototype demonstrates a proposed vertical property representation linked to existing parcel/ULPIN references. It does not issue or modify official ULPIN.
