document.addEventListener("DOMContentLoaded", () => {
    // 1. Initialize MapLibre GL JS
    const map = new maplibregl.Map({
        container: 'map',
        style: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
        center: [77.6200, 12.9300], // Bengaluru AOI Center
        zoom: 15,
        pitch: 60, // Angled for 3D view
        bearing: -20,
        antialias: true
    });

    // Add navigation controls
    map.addControl(new maplibregl.NavigationControl(), 'bottom-right');

    let totalParcels = 0;
    let totalBuildings = 0;

    map.on('load', async () => {
        try {
            // 2. Load GeoJSON Data
            const [parcelsRes, bldgsRes] = await Promise.all([
                fetch('data/cadastral_parcels_valid.geojson'),
                fetch('data/buildings_3d.geojson')
            ]);

            if (!parcelsRes.ok || !bldgsRes.ok) throw new Error("Failed to load data.");

            const parcelsData = await parcelsRes.json();
            const bldgsData = await bldgsRes.json();

            totalParcels = parcelsData.features.length;
            totalBuildings = bldgsData.features.length;

            document.getElementById('stat-parcels').innerText = totalParcels.toLocaleString();
            document.getElementById('stat-buildings').innerText = totalBuildings.toLocaleString();

            // 3. Add Parcels Source & Layer
            map.addSource('parcels', {
                type: 'geojson',
                data: parcelsData
            });

            map.addLayer({
                'id': 'parcels-layer',
                'type': 'fill',
                'source': 'parcels',
                'paint': {
                    'fill-color': '#ffffff',
                    'fill-opacity': 0.05,
                    'fill-outline-color': '#ffffff'
                }
            });

            map.addLayer({
                'id': 'parcels-line-layer',
                'type': 'line',
                'source': 'parcels',
                'paint': {
                    'line-color': '#ffffff',
                    'line-opacity': 0.3,
                    'line-width': 1,
                    'line-dasharray': [2, 2]
                }
            });

            // 4. Add Buildings 3D Source & Layer
            map.addSource('buildings', {
                type: 'geojson',
                data: bldgsData
            });

            map.addLayer({
                'id': 'buildings-3d-layer',
                'type': 'fill-extrusion',
                'source': 'buildings',
                'paint': {
                    // Match Status Color Coding
                    'fill-extrusion-color': [
                        'match',
                        ['get', 'match_status_2d'],
                        'CONTAINED', '#10b981',        // Emerald
                        'MAJORITY', '#f59e0b',         // Amber
                        'BOUNDARY_OVERLAP', '#ef4444', // Red
                        '#64748b'                      // Slate fallback
                    ],
                    // Dynamic 3D Extrusion using Satellite Heights
                    'fill-extrusion-height': ['get', 'building_height_m'],
                    'fill-extrusion-base': 0,
                    'fill-extrusion-opacity': 0.85
                }
            });

            // Hide Loader
            document.getElementById('loader').classList.add('hidden');

            // 5. Interactivity: Click on Building
            map.on('click', 'buildings-3d-layer', (e) => {
                if (!e.features.length) return;
                const feature = e.features[0];
                const props = feature.properties;

                // Update Sidebar Property Card
                const card = document.getElementById('property-card');
                card.style.display = 'block';
                // Trigger reflow for animation
                void card.offsetWidth;
                card.classList.remove('hidden');

                document.getElementById('prop-ulpin').innerText = props.linked_parcel_id || 'NONE';
                document.getElementById('prop-match').innerText = props.match_status_2d || 'UNKNOWN';
                document.getElementById('prop-dem').innerText = props.ground_elevation_m ? `${props.ground_elevation_m} m` : 'N/A';
                
                const h = props.building_height_m || 3.5;
                const fl = props.derived_floors || Math.max(1, Math.round(h / 3.5));
                document.getElementById('prop-floors').innerText = `${h}m (${fl} ${fl === 1 ? 'Floor' : 'Floors'})`;
                document.getElementById('prop-source').innerText = props.height_source || 'GOOGLE_OPEN_BUILDINGS_2.5D';
                
                const aiEl = document.getElementById('prop-ai-status');
                if (props.ai_anomaly_flag) {
                    aiEl.innerText = `ANOMALY DETECTED (${props.ai_anomaly_score})`;
                    aiEl.style.color = 'var(--color-conflict)';
                    aiEl.style.fontWeight = 'bold';
                } else {
                    aiEl.innerText = `NORMAL (${props.ai_anomaly_score || 0})`;
                    aiEl.style.color = 'var(--color-contained)';
                    aiEl.style.fontWeight = 'normal';
                }
                document.getElementById('prop-3d-ulpin').innerText = props.proposed_vertical_ulpin || 'NONE';

                const gateEl = document.getElementById('prop-gate-status');
                const gateStatus = props.final_verification_status || 'PROVISIONAL';
                gateEl.innerText = gateStatus;
                if (gateStatus === 'VERIFIED') {
                    gateEl.style.color = 'var(--color-contained)';
                } else if (gateStatus === 'PROVISIONAL') {
                    gateEl.style.color = 'var(--color-majority)';
                } else {
                    gateEl.style.color = 'var(--color-conflict)';
                }
            });

            // Reviewer Action Handler (Rule 8)
            window.reviewAction = (action) => {
                const gateEl = document.getElementById('prop-gate-status');
                const ulpin = document.getElementById('prop-3d-ulpin').innerText;
                
                if (action === 'APPROVE') {
                    gateEl.innerText = 'REVIEWER_APPROVED';
                    gateEl.style.color = 'var(--color-contained)';
                } else if (action === 'CORRECT') {
                    gateEl.innerText = 'REVIEWER_CORRECTED';
                    gateEl.style.color = 'var(--accent-blue)';
                } else if (action === 'REJECT') {
                    gateEl.innerText = 'REVIEWER_REJECTED';
                    gateEl.style.color = 'var(--color-conflict)';
                } else {
                    gateEl.innerText = 'MARK_UNRESOLVED';
                    gateEl.style.color = 'var(--color-majority)';
                }
                
                console.log(`[AUDIT LOG - RULE 8] Reviewer Action '${action}' recorded for 3D ULPIN: ${ulpin}`);
                alert(`Audit Action Recorded!\nStructure: ${ulpin}\nStatus: ${action}`);
            };

            // Change cursor on hover
            map.on('mouseenter', 'buildings-3d-layer', () => {
                map.getCanvas().style.cursor = 'pointer';
            });
            map.on('mouseleave', 'buildings-3d-layer', () => {
                map.getCanvas().style.cursor = '';
            });

        } catch (error) {
            console.error(error);
            document.getElementById('loader').innerHTML = `<p style="color: #ef4444;">Error loading GIS data. Check console.</p>`;
        }
    });
});
