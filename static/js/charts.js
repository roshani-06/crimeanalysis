// Chart utilities and configurations
class ChartManager {
    constructor() {
        this.colors = [
            '#667eea', '#764ba2', '#f093fb', '#f5576c', 
            '#4facfe', '#00f2fe', '#43e97b', '#38f9d7',
            '#fa709a', '#fee140', '#a8edea', '#fed6e3'
        ];
    }

    createBarChart(elementId, data, options = {}) {
        const { labels, values, title, xLabel, yLabel } = data;
        
        const trace = {
            x: labels,
            y: values,
            type: 'bar',
            marker: {
                color: this.colors,
                line: {
                    color: 'rgba(0,0,0,0.2)',
                    width: 1
                }
            }
        };

        const layout = {
            title: title || '',
            xaxis: {
                title: xLabel || '',
                tickangle: options.tickAngle || 0
            },
            yaxis: {
                title: yLabel || ''
            },
            margin: {
                l: 60,
                r: 40,
                t: 40,
                b: 60
            }
        };

        Plotly.newPlot(elementId, [trace], layout);
    }

    createLineChart(elementId, data, options = {}) {
        const { labels, values, title, xLabel, yLabel } = data;
        
        const trace = {
            x: labels,
            y: values,
            type: 'scatter',
            mode: 'lines+markers',
            line: {
                color: options.color || '#667eea',
                width: 3
            },
            marker: {
                color: options.markerColor || '#764ba2',
                size: 8
            }
        };

        const layout = {
            title: title || '',
            xaxis: {
                title: xLabel || ''
            },
            yaxis: {
                title: yLabel || ''
            }
        };

        Plotly.newPlot(elementId, [trace], layout);
    }

    createPieChart(elementId, data, options = {}) {
        const { labels, values, title } = data;
        
        const trace = {
            labels: labels,
            values: values,
            type: 'pie',
            marker: {
                colors: this.colors
            },
            textinfo: 'label+percent',
            hoverinfo: 'label+value+percent'
        };

        const layout = {
            title: title || '',
            height: options.height || 400,
            showlegend: options.showLegend !== false
        };

        Plotly.newPlot(elementId, [trace], layout);
    }

    createHeatmap(elementId, data, options = {}) {
        const { x, y, z, title } = data;
        
        const trace = {
            x: x,
            y: y,
            z: z,
            type: 'heatmap',
            colorscale: options.colorscale || 'Viridis',
            showscale: true
        };

        const layout = {
            title: title || '',
            xaxis: {
                title: options.xTitle || ''
            },
            yaxis: {
                title: options.yTitle || ''
            }
        };

        Plotly.newPlot(elementId, [trace], layout);
    }

    updateChart(elementId, newData) {
        Plotly.react(elementId, newData.data, newData.layout);
    }

    downloadChart(elementId, filename) {
        Plotly.downloadImage(elementId, {
            format: 'png',
            filename: filename,
            height: 600,
            width: 800
        });
    }
}

// Initialize chart manager
window.chartManager = new ChartManager();