// Map utilities for crime hotspots
class MapManager {
    constructor() {
        this.map = null;
        this.markers = [];
        this.heatmap = null;
        this.init();
    }

    init() {
        // This would be initialized when the map page loads
    }

    createMap(containerId, center = [20.5937, 78.9629], zoom = 5) {
        this.map = L.map(containerId).setView(center, zoom);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 18
        }).addTo(this.map);

        return this.map;
    }

    addCrimeHotspots(hotspotData) {
        // Clear existing markers
        this.clearMarkers();

        // Add new markers
        Object.entries(hotspotData).forEach(([location, crimeCount], index) => {
            const [state, district] = location.split(',');
            const coordinates = this.getCoordinates(district, state);
            
            if (coordinates) {
                const marker = L.circleMarker(coordinates, {
                    radius: this.getRadius(crimeCount),
                    fillColor: this.getColor(crimeCount),
                    color: '#000',
                    weight: 1,
                    opacity: 1,
                    fillOpacity: 0.8
                }).addTo(this.map);

                marker.bindPopup(`
                    <div class="crime-popup">
                        <h6>${district}, ${state}</h6>
                        <p><strong>Crime Count:</strong> ${crimeCount}</p>
                        <p class="text-muted">Click for detailed analysis</p>
                    </div>
                `);

                this.markers.push(marker);
            }
        });
    }

    addHeatmap(heatmapData) {
        const points = [];
        
        Object.entries(heatmapData).forEach(([location, crimeCount]) => {
            const [state, district] = location.split(',');
            const coordinates = this.getCoordinates(district, state);
            
            if (coordinates) {
                // Add multiple points based on crime count for heatmap effect
                for (let i = 0; i < Math.min(crimeCount / 100, 10); i++) {
                    points.push([
                        coordinates[0] + (Math.random() - 0.5) * 0.5,
                        coordinates[1] + (Math.random() - 0.5) * 0.5,
                        crimeCount / 1000
                    ]);
                }
            }
        });

        this.heatmap = L.heatLayer(points, {
            radius: 25,
            blur: 15,
            maxZoom: 17
        }).addTo(this.map);
    }

    getCoordinates(district, state) {
        // Simplified coordinate mapping - in real app, use geocoding API
        const coordinates = {
            'Delhi': [28.7041, 77.1025],
            'Mumbai': [19.0760, 72.8777],
            'Chennai': [13.0827, 80.2707],
            'Kolkata': [22.5726, 88.3639],
            'Bengaluru': [12.9716, 77.5946],
            'Hyderabad': [17.3850, 78.4867],
            'Ahmedabad': [23.0225, 72.5714],
            'Pune': [18.5204, 73.8567],
            'Jaipur': [26.9124, 75.7873],
            'Lucknow': [26.8467, 80.9462]
        };

        return coordinates[district] || coordinates[state] || [20.5937, 78.9629];
    }

    getRadius(crimeCount) {
        return Math.min(Math.max(crimeCount / 100, 5), 30);
    }

    getColor(crimeCount) {
        if (crimeCount > 1000) return '#ff0000';
        if (crimeCount > 500) return '#ff6b00';
        if (crimeCount > 100) return '#ffd000';
        if (crimeCount > 50) return '#a8ff00';
        return '#4cff00';
    }

    clearMarkers() {
        this.markers.forEach(marker => {
            this.map.removeLayer(marker);
        });
        this.markers = [];
        
        if (this.heatmap) {
            this.map.removeLayer(this.heatmap);
            this.heatmap = null;
        }
    }

    fitBounds() {
        if (this.markers.length > 0) {
            const group = new L.featureGroup(this.markers);
            this.map.fitBounds(group.getBounds().pad(0.1));
        }
    }
}

// Initialize map manager
window.mapManager = new MapManager();