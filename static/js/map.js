/**
 * Interactive Map Module for Provincial Reform Portal
 * Handles map visualization of government projects
 */

class ProjectMap {
    constructor(containerId = 'map') {
        this.containerId = containerId;
        this.map = null;
        this.markers = [];
        this.projectData = [];
        this.filteredData = [];
        this.markerClusterGroup = null;
        this.currentPopup = null;
        
        // Map configuration
        this.defaultCenter = [30.3753, 69.3451]; // Pakistan center
        this.defaultZoom = 6;
        this.minZoom = 5;
        this.maxZoom = 18;
        
        // Status colors
        this.statusColors = {
            'COMPLETE': '#198754',
            'ON_TRACK': '#0d6efd',
            'AT_RISK': '#ffc107',
            'DELAYED': '#dc3545'
        };
        
        this.init();
    }

    init() {
        this.initializeMap();
        this.setupEventListeners();
    }

    initializeMap() {
        // Initialize Leaflet map
        this.map = L.map(this.containerId, {
            center: this.defaultCenter,
            zoom: this.defaultZoom,
            minZoom: this.minZoom,
            maxZoom: this.maxZoom,
            zoomControl: true,
            scrollWheelZoom: true
        });

        // Add tile layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: this.maxZoom
        }).addTo(this.map);

        // Add custom controls
        this.addCustomControls();
        
        // Initialize marker cluster group
        this.markerClusterGroup = L.markerClusterGroup({
            maxClusterRadius: 50,
            iconCreateFunction: this.createClusterIcon.bind(this)
        });
        
        this.map.addLayer(this.markerClusterGroup);
    }

    setupEventListeners() {
        // Filter controls
        document.getElementById('sector-filter')?.addEventListener('change', this.applyFilters.bind(this));
        document.getElementById('district-filter')?.addEventListener('change', this.applyFilters.bind(this));
        document.getElementById('status-filter')?.addEventListener('change', this.applyFilters.bind(this));
        document.getElementById('progress-min')?.addEventListener('input', this.applyFilters.bind(this));
        document.getElementById('progress-max')?.addEventListener('input', this.applyFilters.bind(this));

        // Map events
        this.map.on('popupclose', () => {
            this.currentPopup = null;
            this.hideProjectDetails();
        });

        this.map.on('zoomend', this.updateVisibleProjectsCount.bind(this));
        this.map.on('moveend', this.updateVisibleProjectsCount.bind(this));
    }

    addCustomControls() {
        // Fullscreen control
        const fullscreenControl = L.control({position: 'topright'});
        fullscreenControl.onAdd = () => {
            const div = L.DomUtil.create('div', 'leaflet-bar leaflet-control');
            div.innerHTML = '<a href="#" title="Toggle Fullscreen"><i class="bi bi-arrows-fullscreen"></i></a>';
            
            L.DomEvent.on(div.firstChild, 'click', (e) => {
                L.DomEvent.preventDefault(e);
                this.toggleFullscreen();
            });
            
            return div;
        };
        fullscreenControl.addTo(this.map);

        // Legend control
        const legendControl = L.control({position: 'bottomright'});
        legendControl.onAdd = () => {
            const div = L.DomUtil.create('div', 'map-legend');
            div.innerHTML = this.createLegendHTML();
            return div;
        };
        legendControl.addTo(this.map);
    }

    createLegendHTML() {
        const statusLabels = {
            'COMPLETE': 'Complete',
            'ON_TRACK': 'On Track',
            'AT_RISK': 'At Risk',
            'DELAYED': 'Delayed'
        };

        let html = '<div class="legend-content bg-white p-2 border rounded shadow-sm">';
        html += '<h6 class="mb-2">Project Status</h6>';
        
        Object.entries(this.statusColors).forEach(([status, color]) => {
            html += `
                <div class="legend-item d-flex align-items-center mb-1">
                    <div class="legend-color" style="width: 12px; height: 12px; background-color: ${color}; border-radius: 50%; margin-right: 8px;"></div>
                    <span class="small">${statusLabels[status]}</span>
                </div>
            `;
        });
        
        html += '</div>';
        return html;
    }

    loadProjectData(data) {
        this.projectData = data;
        this.filteredData = [...data];
        this.renderMarkers();
        this.updateVisibleProjectsCount();
        
        // Fit map to show all projects if data exists
        if (data.length > 0) {
            this.fitMapToProjects();
        }
    }

    renderMarkers() {
        // Clear existing markers
        this.markerClusterGroup.clearLayers();
        this.markers = [];

        this.filteredData.forEach(project => {
            const marker = this.createProjectMarker(project);
            if (marker) {
                this.markers.push(marker);
                this.markerClusterGroup.addLayer(marker);
            }
        });
    }

    createProjectMarker(project) {
        if (!project.latitude || !project.longitude) {
            return null;
        }

        const color = this.statusColors[project.status] || '#6c757d';
        const size = this.calculateMarkerSize(project.budget_allocated);
        
        const icon = L.divIcon({
            className: 'custom-project-marker',
            html: `
                <div class="marker-content" style="
                    width: ${size}px; 
                    height: ${size}px; 
                    background-color: ${color}; 
                    border: 3px solid white; 
                    border-radius: 50%; 
                    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-weight: bold;
                    font-size: ${Math.max(8, size/3)}px;
                ">
                    ${project.progress || 0}%
                </div>
            `,
            iconSize: [size, size],
            iconAnchor: [size/2, size/2]
        });

        const marker = L.marker([project.latitude, project.longitude], { icon })
            .bindPopup(this.createPopupContent(project), {
                maxWidth: 300,
                className: 'custom-popup'
            });

        marker.on('click', () => {
            this.showProjectDetails(project);
        });

        // Store project data with marker
        marker.projectData = project;
        
        return marker;
    }

    calculateMarkerSize(budget) {
        // Scale marker size based on budget (20-40px range)
        const minSize = 20;
        const maxSize = 40;
        const maxBudget = Math.max(...this.projectData.map(p => p.budget_allocated || 0));
        
        if (maxBudget === 0) return minSize;
        
        const scale = (budget || 0) / maxBudget;
        return Math.round(minSize + (maxSize - minSize) * scale);
    }

    createPopupContent(project) {
        const progressColor = this.getProgressColor(project.progress);
        const statusBadge = this.getStatusBadge(project.status);
        
        return `
            <div class="project-popup">
                <div class="popup-header d-flex align-items-center mb-2">
                    <span class="fs-4 me-2">${project.sector_icon || '📊'}</span>
                    <div class="flex-grow-1">
                        <h6 class="mb-0 fw-bold">${project.name}</h6>
                        <small class="text-muted">${project.district} • ${project.sector}</small>
                    </div>
                </div>
                
                <div class="popup-content">
                    <div class="mb-2">
                        ${statusBadge}
                        <span class="badge bg-light text-dark ms-1">${project.progress || 0}% Complete</span>
                    </div>
                    
                    <div class="progress mb-2" style="height: 6px;">
                        <div class="progress-bar" style="width: ${project.progress || 0}%; background-color: ${progressColor};"></div>
                    </div>
                    
                    <div class="row small text-muted">
                        <div class="col-6">
                            <strong>Budget:</strong><br>
                            PKR ${this.formatBudget(project.budget_allocated)}
                        </div>
                        <div class="col-6">
                            <strong>Spent:</strong><br>
                            ${project.budget_utilization || 0}% used
                        </div>
                    </div>
                    
                    <div class="mt-2 text-center">
                        <button class="btn btn-outline-primary btn-sm" onclick="window.open('/project/${project.id}/', '_blank')">
                            <i class="bi bi-eye me-1"></i>View Details
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    getProgressColor(progress) {
        if (progress >= 80) return '#198754';
        if (progress >= 60) return '#ffc107';
        if (progress >= 30) return '#fd7e14';
        return '#dc3545';
    }

    getStatusBadge(status) {
        const badges = {
            'COMPLETE': '<span class="badge bg-success">Complete</span>',
            'ON_TRACK': '<span class="badge bg-primary">On Track</span>',
            'AT_RISK': '<span class="badge bg-warning">At Risk</span>',
            'DELAYED': '<span class="badge bg-danger">Delayed</span>'
        };
        return badges[status] || '<span class="badge bg-secondary">Unknown</span>';
    }

    formatBudget(amount) {
        if (amount >= 1000000000) {
            return `${(amount / 1000000000).toFixed(1)}B`;
        } else if (amount >= 1000000) {
            return `${(amount / 1000000).toFixed(1)}M`;
        } else if (amount >= 1000) {
            return `${(amount / 1000).toFixed(1)}K`;
        }
        return amount?.toString() || '0';
    }

    createClusterIcon(cluster) {
        const count = cluster.getChildCount();
        let className = 'marker-cluster marker-cluster-';
        
        if (count < 10) {
            className += 'small';
        } else if (count < 100) {
            className += 'medium';
        } else {
            className += 'large';
        }

        return new L.DivIcon({
            html: `<div class="cluster-inner">${count}</div>`,
            className: className,
            iconSize: new L.Point(40, 40)
        });
    }

    applyFilters() {
        const filters = {
            sector: document.getElementById('sector-filter')?.value || '',
            district: document.getElementById('district-filter')?.value || '',
            status: document.getElementById('status-filter')?.value || '',
            progressMin: parseFloat(document.getElementById('progress-min')?.value) || 0,
            progressMax: parseFloat(document.getElementById('progress-max')?.value) || 100
        };

        this.filteredData = this.projectData.filter(project => {
            // Sector filter
            if (filters.sector && project.sector_id != filters.sector) {
                return false;
            }
            
            // District filter
            if (filters.district && project.district_id != filters.district) {
                return false;
            }
            
            // Status filter
            if (filters.status && project.status !== filters.status) {
                return false;
            }
            
            // Progress filter
            const progress = project.progress || 0;
            if (progress < filters.progressMin || progress > filters.progressMax) {
                return false;
            }
            
            return true;
        });

        this.renderMarkers();
        this.updateVisibleProjectsCount();
        
        // Fit map to filtered projects if any exist
        if (this.filteredData.length > 0) {
            this.fitMapToProjects();
        }
    }

    clearFilters() {
        // Reset filter controls
        document.getElementById('sector-filter').value = '';
        document.getElementById('district-filter').value = '';
        document.getElementById('status-filter').value = '';
        document.getElementById('progress-min').value = '';
        document.getElementById('progress-max').value = '';
        
        // Reset filtered data
        this.filteredData = [...this.projectData];
        this.renderMarkers();
        this.updateVisibleProjectsCount();
    }

    fitMapToProjects() {
        if (this.filteredData.length === 0) return;
        
        const bounds = L.latLngBounds();
        this.filteredData.forEach(project => {
            if (project.latitude && project.longitude) {
                bounds.extend([project.latitude, project.longitude]);
            }
        });
        
        if (bounds.isValid()) {
            this.map.fitBounds(bounds, { padding: [20, 20] });
        }
    }

    updateVisibleProjectsCount() {
        const countElement = document.getElementById('visible-projects-count');
        if (countElement) {
            countElement.textContent = this.filteredData.length;
        }
    }

    showProjectDetails(project) {
        const panel = document.getElementById('project-details-panel');
        const title = document.getElementById('selected-project-title');
        const content = document.getElementById('project-details-content');
        
        if (!panel || !title || !content) return;
        
        title.textContent = project.name;
        content.innerHTML = this.createProjectDetailsHTML(project);
        panel.style.display = 'block';
        
        // Scroll to panel
        panel.scrollIntoView({ behavior: 'smooth' });
    }

    createProjectDetailsHTML(project) {
        return `
            <div class="row">
                <div class="col-md-6">
                    <h6 class="fw-bold mb-2">Project Information</h6>
                    <table class="table table-sm table-borderless">
                        <tr>
                            <td class="text-muted">Sector:</td>
                            <td>${project.sector}</td>
                        </tr>
                        <tr>
                            <td class="text-muted">District:</td>
                            <td>${project.district}</td>
                        </tr>
                        <tr>
                            <td class="text-muted">Status:</td>
                            <td>${this.getStatusBadge(project.status)}</td>
                        </tr>
                        <tr>
                            <td class="text-muted">Progress:</td>
                            <td>${project.progress || 0}%</td>
                        </tr>
                    </table>
                </div>
                <div class="col-md-6">
                    <h6 class="fw-bold mb-2">Financial Details</h6>
                    <table class="table table-sm table-borderless">
                        <tr>
                            <td class="text-muted">Budget:</td>
                            <td>PKR ${this.formatBudget(project.budget_allocated)}</td>
                        </tr>
                        <tr>
                            <td class="text-muted">Utilized:</td>
                            <td>${project.budget_utilization || 0}%</td>
                        </tr>
                        <tr>
                            <td class="text-muted">Location:</td>
                            <td>${project.latitude?.toFixed(4)}, ${project.longitude?.toFixed(4)}</td>
                        </tr>
                    </table>
                </div>
            </div>
            <div class="mt-3">
                <div class="progress mb-2" style="height: 8px;">
                    <div class="progress-bar" style="width: ${project.progress || 0}%; background-color: ${this.getProgressColor(project.progress)};"></div>
                </div>
                <div class="d-flex justify-content-between small text-muted">
                    <span>0%</span>
                    <span>${project.progress || 0}% Complete</span>
                    <span>100%</span>
                </div>
            </div>
            <div class="mt-3 text-center">
                <a href="/project/${project.id}/" class="btn btn-primary me-2">
                    <i class="bi bi-eye me-1"></i>Full Details
                </a>
                <button class="btn btn-outline-secondary" onclick="projectMap.focusOnProject(${project.id})">
                    <i class="bi bi-geo-alt me-1"></i>Focus on Map
                </button>
            </div>
        `;
    }

    hideProjectDetails() {
        const panel = document.getElementById('project-details-panel');
        if (panel) {
            panel.style.display = 'none';
        }
    }

    focusOnProject(projectId) {
        const project = this.projectData.find(p => p.id === projectId);
        if (project && project.latitude && project.longitude) {
            this.map.setView([project.latitude, project.longitude], 14);
            
            // Find and open the marker popup
            const marker = this.markers.find(m => m.projectData.id === projectId);
            if (marker) {
                marker.openPopup();
            }
        }
    }

    resetMapView() {
        this.map.setView(this.defaultCenter, this.defaultZoom);
        this.hideProjectDetails();
    }

    toggleFullscreen() {
        const mapContainer = document.getElementById(this.containerId);
        if (!document.fullscreenElement) {
            mapContainer.requestFullscreen().then(() => {
                this.map.invalidateSize();
            });
        } else {
            document.exitFullscreen().then(() => {
                this.map.invalidateSize();
            });
        }
    }

    // Public API methods
    addProject(project) {
        this.projectData.push(project);
        this.filteredData.push(project);
        
        const marker = this.createProjectMarker(project);
        if (marker) {
            this.markers.push(marker);
            this.markerClusterGroup.addLayer(marker);
        }
        
        this.updateVisibleProjectsCount();
    }

    removeProject(projectId) {
        this.projectData = this.projectData.filter(p => p.id !== projectId);
        this.filteredData = this.filteredData.filter(p => p.id !== projectId);
        
        const markerIndex = this.markers.findIndex(m => m.projectData.id === projectId);
        if (markerIndex !== -1) {
            this.markerClusterGroup.removeLayer(this.markers[markerIndex]);
            this.markers.splice(markerIndex, 1);
        }
        
        this.updateVisibleProjectsCount();
    }

    updateProject(updatedProject) {
        const index = this.projectData.findIndex(p => p.id === updatedProject.id);
        if (index !== -1) {
            this.projectData[index] = updatedProject;
            
            const filteredIndex = this.filteredData.findIndex(p => p.id === updatedProject.id);
            if (filteredIndex !== -1) {
                this.filteredData[filteredIndex] = updatedProject;
            }
            
            // Re-render markers to reflect changes
            this.renderMarkers();
        }
    }

    getVisibleProjects() {
        const bounds = this.map.getBounds();
        return this.filteredData.filter(project => {
            if (!project.latitude || !project.longitude) return false;
            return bounds.contains([project.latitude, project.longitude]);
        });
    }

    exportMapData() {
        const visibleProjects = this.getVisibleProjects();
        const csvContent = this.convertToCSV(visibleProjects);
        
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `map_projects_${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
    }

    convertToCSV(data) {
        const headers = ['Name', 'Sector', 'District', 'Status', 'Progress', 'Budget', 'Latitude', 'Longitude'];
        const rows = data.map(project => [
            project.name,
            project.sector,
            project.district,
            project.status,
            project.progress || 0,
            project.budget_allocated || 0,
            project.latitude || '',
            project.longitude || ''
        ]);
        
        return [headers, ...rows].map(row => 
            row.map(cell => `"${cell}"`).join(',')
        ).join('\n');
    }
}

// Global functions for map interaction
function initializeMap(projectData) {
    window.projectMap = new ProjectMap('map');
    if (projectData && projectData.length > 0) {
        window.projectMap.loadProjectData(projectData);
    }
}

function resetMapView() {
    if (window.projectMap) {
        window.projectMap.resetMapView();
    }
}

function applyFilters() {
    if (window.projectMap) {
        window.projectMap.applyFilters();
    }
}

function clearFilters() {
    if (window.projectMap) {
        window.projectMap.clearFilters();
    }
}

function closeProjectDetails() {
    if (window.projectMap) {
        window.projectMap.hideProjectDetails();
    }
}

// Export map data function
function exportMapData() {
    if (window.projectMap) {
        window.projectMap.exportMapData();
    }
}
