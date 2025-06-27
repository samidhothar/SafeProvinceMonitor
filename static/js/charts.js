/**
 * Charts Module for Provincial Reform Portal
 * Handles all chart visualizations using Chart.js
 */

class ChartManager {
    constructor() {
        this.charts = new Map();
        this.defaultColors = {
            primary: '#0d6efd',
            secondary: '#6c757d',
            success: '#198754',
            danger: '#dc3545',
            warning: '#ffc107',
            info: '#0dcaf0',
            light: '#f8f9fa',
            dark: '#212529'
        };
        
        this.gradients = {};
        this.animationDuration = 1000;
        
        this.init();
    }

    init() {
        // Set Chart.js global defaults
        this.setGlobalDefaults();
        
        // Create gradients for charts
        this.setupGradients();
        
        // Setup responsive handling
        this.setupResponsiveHandling();
    }

    setGlobalDefaults() {
        Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
        Chart.defaults.font.size = 12;
        Chart.defaults.color = '#6c757d';
        Chart.defaults.responsive = true;
        Chart.defaults.maintainAspectRatio = false;
        Chart.defaults.animation.duration = this.animationDuration;
        Chart.defaults.elements.arc.borderWidth = 0;
        Chart.defaults.elements.bar.borderRadius = 4;
        Chart.defaults.elements.line.tension = 0.4;
        Chart.defaults.elements.point.radius = 4;
        Chart.defaults.elements.point.hoverRadius = 6;
    }

    setupGradients() {
        // Create a temporary canvas to generate gradients
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        // Primary gradient
        this.gradients.primary = ctx.createLinearGradient(0, 0, 0, 400);
        this.gradients.primary.addColorStop(0, 'rgba(13, 110, 253, 0.8)');
        this.gradients.primary.addColorStop(1, 'rgba(13, 110, 253, 0.1)');
        
        // Success gradient
        this.gradients.success = ctx.createLinearGradient(0, 0, 0, 400);
        this.gradients.success.addColorStop(0, 'rgba(25, 135, 84, 0.8)');
        this.gradients.success.addColorStop(1, 'rgba(25, 135, 84, 0.1)');
        
        // Warning gradient
        this.gradients.warning = ctx.createLinearGradient(0, 0, 0, 400);
        this.gradients.warning.addColorStop(0, 'rgba(255, 193, 7, 0.8)');
        this.gradients.warning.addColorStop(1, 'rgba(255, 193, 7, 0.1)');
        
        // Danger gradient
        this.gradients.danger = ctx.createLinearGradient(0, 0, 0, 400);
        this.gradients.danger.addColorStop(0, 'rgba(220, 53, 69, 0.8)');
        this.gradients.danger.addColorStop(1, 'rgba(220, 53, 69, 0.1)');
    }

    setupResponsiveHandling() {
        window.addEventListener('resize', this.debounce(() => {
            this.charts.forEach(chart => {
                chart.resize();
            });
        }, 250));
    }

    // Utility function for debouncing
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
    }

    // Create dynamic gradient for canvas context
    createGradient(ctx, color1, color2, direction = 'vertical') {
        let gradient;
        
        if (direction === 'vertical') {
            gradient = ctx.createLinearGradient(0, 0, 0, ctx.canvas.height);
        } else {
            gradient = ctx.createLinearGradient(0, 0, ctx.canvas.width, 0);
        }
        
        gradient.addColorStop(0, color1);
        gradient.addColorStop(1, color2);
        
        return gradient;
    }

    // Budget Chart (Doughnut)
    createBudgetChart(canvasId, allocated, spent, options = {}) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas with id '${canvasId}' not found`);
            return null;
        }

        const ctx = canvas.getContext('2d');
        const remaining = Math.max(0, allocated - spent);
        
        const config = {
            type: 'doughnut',
            data: {
                labels: ['Spent', 'Remaining'],
                datasets: [{
                    data: [spent, remaining],
                    backgroundColor: [
                        this.defaultColors.success,
                        this.defaultColors.light
                    ],
                    borderWidth: 0,
                    cutout: '70%'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            font: {
                                size: 11
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const percentage = ((value / allocated) * 100).toFixed(1);
                                return `${label}: PKR ${this.formatCurrency(value)} (${percentage}%)`;
                            }
                        }
                    }
                },
                ...options
            }
        };

        const chart = new Chart(ctx, config);
        this.charts.set(canvasId, chart);
        return chart;
    }

    // Progress Chart (Doughnut with center text)
    createProgressChart(canvasId, progress, options = {}) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas with id '${canvasId}' not found`);
            return null;
        }

        const ctx = canvas.getContext('2d');
        const remaining = 100 - progress;
        
        const config = {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [progress, remaining],
                    backgroundColor: [
                        this.defaultColors.primary,
                        this.defaultColors.light
                    ],
                    borderWidth: 0,
                    cutout: '80%'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        enabled: false
                    }
                },
                ...options
            }
        };

        const chart = new Chart(ctx, config);
        this.charts.set(canvasId, chart);
        return chart;
    }

    // KPI Timeline Chart (Line)
    createKPIChart(canvasId, data, target, options = {}) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas with id '${canvasId}' not found`);
            return null;
        }

        const ctx = canvas.getContext('2d');
        
        // Create gradient for the area fill
        const gradient = this.createGradient(ctx, 
            'rgba(13, 110, 253, 0.3)', 
            'rgba(13, 110, 253, 0.05)'
        );

        const config = {
            type: 'line',
            data: {
                labels: data.map(d => d.date),
                datasets: [{
                    label: 'KPI Achievement',
                    data: data.map(d => d.value),
                    borderColor: this.defaultColors.primary,
                    backgroundColor: gradient,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: this.defaultColors.primary,
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }, {
                    label: 'Target',
                    data: data.map(() => target),
                    borderColor: this.defaultColors.danger,
                    backgroundColor: 'transparent',
                    borderDash: [5, 5],
                    fill: false,
                    pointRadius: 0,
                    pointHoverRadius: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 20
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: this.defaultColors.primary,
                        borderWidth: 1,
                        callbacks: {
                            label: (context) => {
                                const label = context.dataset.label || '';
                                const value = context.parsed.y || 0;
                                return `${label}: ${value.toFixed(1)}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            font: {
                                size: 11
                            }
                        }
                    },
                    y: {
                        beginAtZero: true,
                        max: Math.max(target * 1.1, Math.max(...data.map(d => d.value)) * 1.1),
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        ticks: {
                            font: {
                                size: 11
                            }
                        }
                    }
                },
                ...options
            }
        };

        const chart = new Chart(ctx, config);
        this.charts.set(canvasId, chart);
        return chart;
    }

    // Sector Distribution Chart (Pie)
    createSectorChart(canvasId, data, options = {}) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas with id '${canvasId}' not found`);
            return null;
        }

        const ctx = canvas.getContext('2d');
        
        // Generate colors for sectors
        const colors = this.generateColorPalette(data.length);
        
        const config = {
            type: 'pie',
            data: {
                labels: data.map(d => d.name),
                datasets: [{
                    data: data.map(d => d.value),
                    backgroundColor: colors,
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            padding: 15,
                            usePointStyle: true,
                            font: {
                                size: 11
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                },
                ...options
            }
        };

        const chart = new Chart(ctx, config);
        this.charts.set(canvasId, chart);
        return chart;
    }

    // Project Status Chart (Bar)
    createStatusChart(canvasId, data, options = {}) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas with id '${canvasId}' not found`);
            return null;
        }

        const ctx = canvas.getContext('2d');
        
        const statusColors = {
            'Complete': this.defaultColors.success,
            'On Track': this.defaultColors.primary,
            'At Risk': this.defaultColors.warning,
            'Delayed': this.defaultColors.danger
        };

        const config = {
            type: 'bar',
            data: {
                labels: data.map(d => d.status),
                datasets: [{
                    label: 'Projects',
                    data: data.map(d => d.count),
                    backgroundColor: data.map(d => statusColors[d.status] || this.defaultColors.secondary),
                    borderRadius: 4,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const value = context.parsed.y || 0;
                                return `Projects: ${value}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            font: {
                                size: 11
                            }
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        ticks: {
                            stepSize: 1,
                            font: {
                                size: 11
                            }
                        }
                    }
                },
                ...options
            }
        };

        const chart = new Chart(ctx, config);
        this.charts.set(canvasId, chart);
        return chart;
    }

    // Budget Utilization Chart (Horizontal Bar)
    createBudgetUtilizationChart(canvasId, data, options = {}) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas with id '${canvasId}' not found`);
            return null;
        }

        const ctx = canvas.getContext('2d');

        const config = {
            type: 'bar',
            data: {
                labels: data.map(d => d.name),
                datasets: [{
                    label: 'Utilization %',
                    data: data.map(d => d.utilization),
                    backgroundColor: data.map(d => {
                        if (d.utilization > 100) return this.defaultColors.danger;
                        if (d.utilization > 80) return this.defaultColors.warning;
                        return this.defaultColors.success;
                    }),
                    borderRadius: 4,
                    borderSkipped: false
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const value = context.parsed.x || 0;
                                return `Utilization: ${value.toFixed(1)}%`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        max: Math.max(100, Math.max(...data.map(d => d.utilization)) * 1.1),
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        ticks: {
                            callback: (value) => `${value}%`,
                            font: {
                                size: 11
                            }
                        }
                    },
                    y: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            font: {
                                size: 11
                            }
                        }
                    }
                },
                ...options
            }
        };

        const chart = new Chart(ctx, config);
        this.charts.set(canvasId, chart);
        return chart;
    }

    // Timeline Chart (Line with multiple datasets)
    createTimelineChart(canvasId, datasets, options = {}) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas with id '${canvasId}' not found`);
            return null;
        }

        const ctx = canvas.getContext('2d');
        
        // Process datasets with different colors
        const colors = [
            this.defaultColors.primary,
            this.defaultColors.success,
            this.defaultColors.warning,
            this.defaultColors.danger,
            this.defaultColors.info
        ];

        const processedDatasets = datasets.map((dataset, index) => ({
            label: dataset.label,
            data: dataset.data,
            borderColor: colors[index % colors.length],
            backgroundColor: colors[index % colors.length] + '20',
            fill: false,
            tension: 0.4,
            pointRadius: 3,
            pointHoverRadius: 5
        }));

        const config = {
            type: 'line',
            data: {
                labels: datasets[0]?.labels || [],
                datasets: processedDatasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 20
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: this.defaultColors.primary,
                        borderWidth: 1
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            font: {
                                size: 11
                            }
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        ticks: {
                            font: {
                                size: 11
                            }
                        }
                    }
                },
                ...options
            }
        };

        const chart = new Chart(ctx, config);
        this.charts.set(canvasId, chart);
        return chart;
    }

    // Update chart data
    updateChart(canvasId, newData, newLabels = null) {
        const chart = this.charts.get(canvasId);
        if (!chart) {
            console.error(`Chart with id '${canvasId}' not found`);
            return;
        }

        if (newLabels) {
            chart.data.labels = newLabels;
        }

        if (Array.isArray(newData)) {
            chart.data.datasets[0].data = newData;
        } else if (typeof newData === 'object') {
            Object.keys(newData).forEach(key => {
                if (chart.data.datasets[key]) {
                    chart.data.datasets[key].data = newData[key];
                }
            });
        }

        chart.update('active');
    }

    // Destroy chart
    destroyChart(canvasId) {
        const chart = this.charts.get(canvasId);
        if (chart) {
            chart.destroy();
            this.charts.delete(canvasId);
        }
    }

    // Destroy all charts
    destroyAllCharts() {
        this.charts.forEach(chart => chart.destroy());
        this.charts.clear();
    }

    // Get chart instance
    getChart(canvasId) {
        return this.charts.get(canvasId);
    }

    // Utility: Generate color palette
    generateColorPalette(count) {
        const baseColors = [
            this.defaultColors.primary,
            this.defaultColors.success,
            this.defaultColors.warning,
            this.defaultColors.danger,
            this.defaultColors.info,
            '#6f42c1', // Purple
            '#fd7e14', // Orange
            '#20c997', // Teal
            '#e83e8c', // Pink
            '#6c757d'  // Gray
        ];

        if (count <= baseColors.length) {
            return baseColors.slice(0, count);
        }

        // Generate additional colors using HSL
        const colors = [...baseColors];
        const hueStep = 360 / count;
        
        for (let i = baseColors.length; i < count; i++) {
            const hue = (i * hueStep) % 360;
            colors.push(`hsl(${hue}, 70%, 50%)`);
        }

        return colors;
    }

    // Utility: Format currency
    formatCurrency(amount) {
        if (amount >= 1000000000) {
            return `${(amount / 1000000000).toFixed(1)}B`;
        } else if (amount >= 1000000) {
            return `${(amount / 1000000).toFixed(1)}M`;
        } else if (amount >= 1000) {
            return `${(amount / 1000).toFixed(1)}K`;
        }
        return amount.toString();
    }

    // Animation utilities
    animateChart(canvasId, duration = null) {
        const chart = this.charts.get(canvasId);
        if (chart) {
            chart.update(duration || this.animationDuration);
        }
    }

    // Export chart as image
    exportChart(canvasId, filename = 'chart') {
        const chart = this.charts.get(canvasId);
        if (chart) {
            const url = chart.toBase64Image();
            const link = document.createElement('a');
            link.download = `${filename}.png`;
            link.href = url;
            link.click();
        }
    }

    // Responsive chart resizing
    resizeChart(canvasId) {
        const chart = this.charts.get(canvasId);
        if (chart) {
            chart.resize();
        }
    }

    // Theme switching support
    updateTheme(isDark) {
        const textColor = isDark ? '#f8f9fa' : '#6c757d';
        const gridColor = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.05)';

        Chart.defaults.color = textColor;
        
        this.charts.forEach(chart => {
            // Update grid colors
            if (chart.options.scales) {
                Object.keys(chart.options.scales).forEach(scaleId => {
                    if (chart.options.scales[scaleId].grid) {
                        chart.options.scales[scaleId].grid.color = gridColor;
                    }
                    if (chart.options.scales[scaleId].ticks) {
                        chart.options.scales[scaleId].ticks.color = textColor;
                    }
                });
            }
            
            // Update legend colors
            if (chart.options.plugins?.legend?.labels) {
                chart.options.plugins.legend.labels.color = textColor;
            }
            
            chart.update('none');
        });
    }
}

// Initialize chart manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chartManager = new ChartManager();
});

// Global chart utility functions
window.createBudgetChart = (canvasId, allocated, spent, options) => {
    return window.chartManager?.createBudgetChart(canvasId, allocated, spent, options);
};

window.createProgressChart = (canvasId, progress, options) => {
    return window.chartManager?.createProgressChart(canvasId, progress, options);
};

window.createKPIChart = (canvasId, data, target, options) => {
    return window.chartManager?.createKPIChart(canvasId, data, target, options);
};

window.createSectorChart = (canvasId, data, options) => {
    return window.chartManager?.createSectorChart(canvasId, data, options);
};

window.createStatusChart = (canvasId, data, options) => {
    return window.chartManager?.createStatusChart(canvasId, data, options);
};

window.updateChart = (canvasId, newData, newLabels) => {
    return window.chartManager?.updateChart(canvasId, newData, newLabels);
};

window.destroyChart = (canvasId) => {
    return window.chartManager?.destroyChart(canvasId);
};

window.exportChart = (canvasId, filename) => {
    return window.chartManager?.exportChart(canvasId, filename);
};
