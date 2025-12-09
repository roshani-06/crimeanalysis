// Main JavaScript file for Crime Analytics

class CrimeAnalytics {
    constructor() {
        this.currentState = 'All';
        this.currentCrimeType = 'Total_Crimes';
        this.currentYear = 2014;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadInitialData();
    }

    bindEvents() {
        // Navigation active state
        this.setActiveNav();
        
        // Form submissions
        this.bindFormSubmissions();
        
        // Filter changes
        this.bindFilterChanges();
    }

    setActiveNav() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav-link');
        
        navLinks.forEach(link => {
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    }

    bindFormSubmissions() {
        // Analysis form
        const analysisForm = document.getElementById('analysisForm');
        if (analysisForm) {
            analysisForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleAnalysisSubmit();
            });
        }

        // Prediction form
        const predictionForm = document.getElementById('predictionForm');
        if (predictionForm) {
            predictionForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handlePredictionSubmit();
            });
        }
    }

    bindFilterChanges() {
        // State change for districts
        const stateSelect = document.getElementById('stateSelect');
        if (stateSelect) {
            stateSelect.addEventListener('change', (e) => {
                this.loadDistricts(e.target.value);
            });
        }

        // Real-time filter updates
        const filters = document.querySelectorAll('select[name="state"], select[name="crime_type"], select[name="year"]');
        filters.forEach(filter => {
            filter.addEventListener('change', () => {
                if (window.location.pathname === '/analysis') {
                    this.handleAnalysisSubmit();
                }
            });
        });
    }

    async loadInitialData() {
        // Load quick stats on homepage
        if (window.location.pathname === '/') {
            await this.loadQuickStats();
        }
    }

    async loadQuickStats() {
        try {
            const response = await fetch('/analysis?state=All&crime_type=Total_Crimes&year=2014');
            const data = await response.json();
            
            document.getElementById('totalCrimes').textContent = 
                data.total_crimes ? this.formatNumber(data.total_crimes) : '50,000+';
            document.getElementById('statesCovered').textContent = '36';
            document.getElementById('districtsCovered').textContent = '700+';
            document.getElementById('crimeTypes').textContent = '13';
        } catch (error) {
            console.error('Error loading quick stats:', error);
        }
    }

    async handleAnalysisSubmit() {
        const form = document.getElementById('analysisForm');
        const formData = new FormData(form);
        const params = new URLSearchParams(formData);
        
        this.showLoading('results');
        
        try {
            const response = await fetch('/analysis?' + params);
            const data = await response.json();
            this.updateAnalysisCharts(data);
        } catch (error) {
            console.error('Error loading analysis:', error);
            this.showError('results', 'Failed to load analysis data');
        }
    }

    async handlePredictionSubmit() {
        const form = document.getElementById('predictionForm');
        const formData = new FormData(form);
        const data = {
            state: formData.get('state'),
            district: formData.get('district'),
            crime_type: formData.get('crime_type'),
            year: parseInt(formData.get('year'))
        };
        
        this.showLoading('predictionResult');
        
        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            this.displayPredictionResult(result);
        } catch (error) {
            console.error('Error making prediction:', error);
            this.showError('predictionResult', 'Failed to generate prediction');
        }
    }

    async loadDistricts(state) {
        const districtSelect = document.getElementById('districtSelect');
        
        if (!state) {
            districtSelect.disabled = true;
            districtSelect.innerHTML = '<option value="">Select District</option>';
            return;
        }
        
        districtSelect.disabled = true;
        districtSelect.innerHTML = '<option value="">Loading districts...</option>';
        
        try {
            const response = await fetch('/get_districts?state=' + state);
            const districts = await response.json();
            
            districtSelect.innerHTML = '<option value="">Select District</option>';
            districts.forEach(district => {
                const option = document.createElement('option');
                option.value = district;
                option.textContent = district;
                districtSelect.appendChild(option);
            });
            
            districtSelect.disabled = false;
        } catch (error) {
            console.error('Error loading districts:', error);
            districtSelect.innerHTML = '<option value="">Error loading districts</option>';
        }
    }

    updateAnalysisCharts(data) {
        // Update top districts chart
        this.updateTopDistrictsChart(data.top_districts);
        
        // Update stats info
        this.updateStatsInfo(data);
        
        // Update trend chart
        this.updateTrendChart(data.yearly_trend);
    }

    updateTopDistrictsChart(districts) {
        const crimeType = document.getElementById('crimeTypeSelect').value;
        const labels = districts.map(d => d.District);
        const values = districts.map(d => d[crimeType]);
        
        const trace = {
            x: values,
            y: labels,
            type: 'bar',
            orientation: 'h',
            marker: {
                color: 'rgba(102, 126, 234, 0.8)'
            }
        };
        
        const layout = {
            title: 'Top Districts by Crime Rate',
            margin: { l: 150, r: 50, t: 50, b: 50 },
            xaxis: { title: 'Number of Crimes' },
            yaxis: { automargin: true }
        };
        
        Plotly.newPlot('topDistrictsChart', [trace], layout);
    }

    updateStatsInfo(data) {
        const statsDiv = document.getElementById('statsInfo');
        if (statsDiv) {
            statsDiv.innerHTML = `
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number text-primary">${this.formatNumber(data.total_crimes)}</div>
                        <div class="stat-label">Total Crimes</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number text-success">${Math.round(data.avg_crimes)}</div>
                        <div class="stat-label">Average per District</div>
                    </div>
                </div>
            `;
        }
    }

    updateTrendChart(trendData) {
        const years = Object.keys(trendData);
        const values = Object.values(trendData);
        
        const trace = {
            x: years,
            y: values,
            type: 'scatter',
            mode: 'lines+markers',
            line: { color: '#764ba2', width: 3 },
            marker: { color: '#667eea', size: 8 }
        };
        
        const layout = {
            title: 'Yearly Crime Trend',
            xaxis: { title: 'Year' },
            yaxis: { title: 'Number of Crimes' }
        };
        
        Plotly.newPlot('trendChart', [trace], layout);
    }

    displayPredictionResult(result) {
        const resultDiv = document.getElementById('predictionResult');
        const confidenceClass = `confidence-${result.confidence}`;
        
        resultDiv.innerHTML = `
            <div class="prediction-result fade-in">
                <h4>Prediction Results</h4>
                <div class="prediction-details mb-4">
                    <p><strong>Location:</strong> ${result.district}, ${result.state}</p>
                    <p><strong>Crime Type:</strong> ${result.crime_type}</p>
                    <p><strong>Year:</strong> ${result.year}</p>
                </div>
                <div class="prediction-value">${Math.round(result.predicted_crimes)}</div>
                <span class="confidence-badge ${confidenceClass}">
                    ${result.confidence} Confidence
                </span>
            </div>
        `;
    }

    showLoading(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `
                <div class="text-center py-4">
                    <div class="loading"></div>
                    <p class="mt-3 text-muted">Loading...</p>
                </div>
            `;
        }
    }

    showError(elementId, message) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle"></i>
                    ${message}
                </div>
            `;
        }
    }

    formatNumber(num) {
        return new Intl.NumberFormat().format(num);
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    window.crimeAnalytics = new CrimeAnalytics();
});

// Utility functions
const Utils = {
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    formatDate(date) {
        return new Date(date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    },

    downloadCSV(data, filename) {
        const csvContent = "data:text/csv;charset=utf-8," + data;
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", filename);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
};