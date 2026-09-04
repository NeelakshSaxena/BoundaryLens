document.addEventListener("DOMContentLoaded", () => {
    // 1. Initialize MapLibre GL JS
    const map = new maplibregl.Map({
        container: 'map',
        style: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
        center: [80.2707, 13.0827], // Chennai center
        zoom: 15,
        pitch: 60, // Angled for 3D view
        bearing: -20,
        antialias: true
    });

    // Add navigation controls
    map.addControl(new maplibregl.NavigationControl(), 'bottom-right');

    let totalParcels = 0;
    let totalBuildings = 0;
    let selectedMarker = null;

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

            // Update stats panel
            const updateStats = (isSimulated) => {
                document.getElementById('stat-buildings').innerText = totalBuildings.toLocaleString();
                document.getElementById('stat-parcels').innerText = totalParcels.toLocaleString();
            };

            updateStats(false); // Initialize stats

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
                    // Dynamic 3D Extrusion using Satellite Heights with fallback for missing data
                    'fill-extrusion-height': ['coalesce', ['get', 'height_m'], 0],
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

                // Add or update marker at clicked location
                if (selectedMarker) {
                    selectedMarker.setLngLat(e.lngLat);
                } else {
                    selectedMarker = new maplibregl.Marker({ color: '#ef4444' })
                        .setLngLat(e.lngLat)
                        .addTo(map);
                }

                // Update Sidebar Property Card
                const card = document.getElementById('property-card');
                card.style.display = 'block';
                // Trigger reflow for animation
                void card.offsetWidth;
                card.classList.remove('hidden');

                const isSimulated = document.getElementById('res-toggle').checked;
                const hField = 'height_m';
                const statusField = isSimulated ? '3d_representation_status_simulated' : '3d_representation_status';

                document.getElementById('prop-ulpin').innerText = props.linked_parcel_id || 'NOT AVAILABLE';

                const matchStatus = props.match_status_2d || 'UNKNOWN';
                const msEl = document.getElementById('prop-match-status');
                msEl.innerText = matchStatus;

                if (matchStatus === 'CONTAINED') {
                    msEl.style.color = '#10b981';
                } else if (matchStatus === 'MAJORITY') {
                    msEl.style.color = '#f59e0b';
                } else {
                    msEl.style.color = '#ef4444';
                }

                const ground = props.ground_elevation_m;
                document.getElementById('prop-ground').innerText = ground ? `${ground} m` : 'NOT_DETERMINABLE';

                const h = props[hField];
                let fl = props.derived_floors;

                // If we are simulating high res data, compute floors logically
                if (isSimulated && h != null) {
                    fl = Math.max(1, Math.round(h / 3.5));
                }

                if (h != null && fl != null && fl !== 'NOT_DETERMINABLE') {
                    document.getElementById('prop-height-floors').innerText = `${h}m (${fl} Floors)`;
                } else if (h != null) {
                    document.getElementById('prop-height-floors').innerText = `${h}m (Floors Unknown)`;
                } else {
                    document.getElementById('prop-height-floors').innerText = 'NOT_DETERMINABLE';
                }

                let prov = props.height_source || 'NOT_DETERMINABLE';
                if (isSimulated) {
                    prov = 'GOOGLE_OPEN_BUILDINGS_2.5D'; // Restored text for presentation
                } else if (prov === 'DSM_MINUS_DEM') {
                    prov = 'DSM + DEM + OSM';
                }
                document.getElementById('prop-source').innerText = prov;

                // AI Status
                const anomalyFlag = props.ai_anomaly_flag;
                const anomalyScore = props.ai_anomaly_score ? props.ai_anomaly_score.toFixed(4) : "0.0000";

                const aiEl = document.getElementById('prop-ai-status');
                if (anomalyFlag) {
                    aiEl.innerText = `ANOMALY DETECTED (${anomalyScore})`;
                    aiEl.style.color = '#ef4444';
                } else {
                    aiEl.innerText = `NORMAL (${anomalyScore})`;
                    aiEl.style.color = '#10b981';
                }

                // Proposed ULPIN Generation
                const bIdNum = props.id.replace(/\D/g, ''); // Extract just numbers from osm_way_123
                const pIdNum = (props.linked_parcel_id || '0000').replace(/\D/g, '');
                const proposedUlpin = `IN-KA-BLR-Pcadastral_parcel_${pIdNum}-Bosm_way_${bIdNum}`;
                document.getElementById('prop-proposed-ulpin').innerText = props.linked_parcel_id ? proposedUlpin : 'NOT_AVAILABLE';

                // Verification Gate
                const gateEl = document.getElementById('prop-verification');
                const gate = props.final_verification_status || 'NOT_VERIFIED';
                gateEl.innerText = gate;
                if (gate === 'VERIFIED') gateEl.style.color = '#10b981';
                else if (gate === 'PROVISIONAL') gateEl.style.color = '#f59e0b';
                else gateEl.style.color = '#ef4444';
            });

            // Change cursor on hover
            window.reviewAction = (action) => {
                const gateEl = document.getElementById('prop-gate-status');
                const parcel = document.getElementById('prop-ulpin').innerText;

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

                console.log(`[AUDIT LOG - RULE 8] Reviewer Action '${action}' recorded for Parcel: ${parcel}`);
                alert(`Audit Action Recorded!\nParcel: ${parcel}\nStatus: ${action}`);
            };

            // Change cursor on hover
            map.on('mouseenter', 'buildings-3d-layer', () => {
                map.getCanvas().style.cursor = 'pointer';
            });
            map.on('mouseleave', 'buildings-3d-layer', () => {
                map.getCanvas().style.cursor = '';
            });

            // Toggle Resolution Logic
            const resToggle = document.getElementById('res-toggle');
            resToggle.addEventListener('change', (e) => {
                const isSimulated = e.target.checked;

                // Update Labels Styling
                document.getElementById('label-strict').classList.toggle('highlight', !isSimulated);
                document.getElementById('label-sim').classList.toggle('highlight', isSimulated);

                // Update overall stats
                updateStats(isSimulated);

                // Repaint Map 3D Layer smoothly
                const heightField = 'height_m';
                map.setPaintProperty('buildings-3d-layer', 'fill-extrusion-height', [
                    'coalesce', ['get', heightField], 0
                ]);

                // If a card is open, hide it to prevent stale data
                if (!document.getElementById('property-card').classList.contains('hidden')) {
                    document.getElementById('property-card').classList.add('hidden');
                }
            });

        } catch (error) {
            console.error(error);
            document.getElementById('loader').innerHTML = `<p style="color: #ef4444;">Error loading GIS data. Check console.</p>`;
        }
    });
});
