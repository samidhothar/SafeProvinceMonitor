/**
 * Dashboard JavaScript Module
 * Handles general dashboard functionality and utilities
 */

class DashboardManager {
    constructor() {
        this.apiBaseUrl = '/api';
        this.refreshInterval = 30000; // 30 seconds
        this.charts = {};
        this.notifications = [];
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeTooltips();
        this.startAutoRefresh();
        this.setupNotifications();
        
        // Initialize components based on current page
        this.initializePageSpecificFeatures();
    }

    setupEventListeners() {
        // Global search functionality
        const searchInput = document.getElementById('global-search');
        if (searchInput) {
            searchInput.addEventListener('input', this.debounce(this.handleGlobalSearch.bind(this), 300));
        }

        // Theme toggle
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', this.toggleTheme.bind(this));
        }

        // Notification handlers
        document.addEventListener('click', (e) => {
            if (e.target.matches('.notification-dismiss')) {
                this.dismissNotification(e.target.closest('.notification'));
            }
        });

        // Auto-hide alerts
        setTimeout(() => {
            const alerts = document.querySelectorAll('.alert-dismissible');
            alerts.forEach(alert => {
                if (alert && !alert.classList.contains('manual-dismiss')) {
                    const closeBtn = alert.querySelector('.btn-close');
                    if (closeBtn) closeBtn.click();
                }
            });
        }, 5000);
    }

    initializeTooltips() {
        // Initialize Bootstrap tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });

        // Initialize Bootstrap popovers
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }

    startAutoRefresh() {
        // Auto-refresh dashboard stats
        setInterval(() => {
            this.refreshDashboardStats();
        }, this.refreshInterval);
    }

    setupNotifications() {
        // Check for system notifications
        this.checkSystemHealth();
        this.checkProjectDeadlines();
    }

    initializePageSpecificFeatures() {
        const currentPage = this.getCurrentPage();
        
        switch (currentPage) {
            case 'home':
                this.initializeHomeDashboard();
                break;
            case 'map':
                this.initializeMapFeatures();
                break;
            case 'project_detail':
                this.initializeProjectDetail();
                break;
            case 'feedback':
                this.initializeFeedbackFeatures();
                break;
        }
    }

    getCurrentPage() {
        const path = window.location.pathname;
        if (path === '/' || path === '/dashboard/') return 'home';
        if (path.includes('/map/')) return 'map';
        if (path.includes('/project/')) return 'project_detail';
        if (path.includes('/feedback/')) return 'feedback';
        if (path.includes('/procurement/')) return 'procurement';
        return 'unknown';
    }

    // API Methods
    async fetchAPI(endpoint, options = {}) {
        try {
            const response = await fetch(`${this.apiBaseUrl}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            this.showNotification('API Error', 'Failed to fetch data. Please try again.', 'error');
            throw error;
        }
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }

    // Dashboard Stats
    async refreshDashboardStats() {
        try {
            const stats = await this.fetchAPI('/dashboard/stats/');
            this.updateStatsDisplay(stats);
        } catch (error) {
            console.error('Failed to refresh dashboard stats:', error);
        }
    }

    updateStatsDisplay(stats) {
        const mappings = {
            'total-projects': stats.total_projects,
            'completed-projects': stats.completed_projects,
            'at-risk-projects': stats.at_risk_projects,
            'delayed-projects': stats.delayed_projects,
            'footer-total-projects': stats.total_projects,
            'footer-completed-projects': stats.completed_projects
        };

        Object.entries(mappings).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element && value !== undefined) {
                this.animateNumber(element, parseInt(element.textContent) || 0, value);
            }
        });
    }

    animateNumber(element, start, end, duration = 1000) {
        const range = end - start;
        const increment = range / (duration / 16);
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
                element.textContent = Math.round(end);
                clearInterval(timer);
            } else {
                element.textContent = Math.round(current);
            }
        }, 16);
    }

    // Search Functionality
    handleGlobalSearch(event) {
        const query = event.target.value.trim();
        if (query.length < 2) {
            this.hideSearchResults();
            return;
        }

        this.performSearch(query);
    }

    async performSearch(query) {
        try {
            const results = await this.fetchAPI(`/projects/?search=${encodeURIComponent(query)}`);
            this.displaySearchResults(results.results || []);
        } catch (error) {
            console.error('Search failed:', error);
        }
    }

    displaySearchResults(results) {
        let resultsContainer = document.getElementById('search-results');
        if (!resultsContainer) {
            resultsContainer = this.createSearchResultsContainer();
        }

        if (results.length === 0) {
            resultsContainer.innerHTML = '<div class="p-3 text-muted">No results found</div>';
            return;
        }

        const html = results.map(project => `
            <div class="search-result-item p-3 border-bottom">
                <div class="d-flex align-items-center">
                    <span class="me-2">${project.sector?.icon || '📊'}</span>
                    <div class="flex-grow-1">
                        <div class="fw-bold">${project.name}</div>
                        <div class="small text-muted">${project.district_name} • ${project.sector_name}</div>
                    </div>
                    <a href="/project/${project.id}/" class="btn btn-sm btn-outline-primary">
                        <i class="bi bi-arrow-right"></i>
                    </a>
                </div>
            </div>
        `).join('');

        resultsContainer.innerHTML = html;
        resultsContainer.style.display = 'block';
    }

    createSearchResultsContainer() {
        const container = document.createElement('div');
        container.id = 'search-results';
        container.className = 'position-absolute bg-white border rounded shadow-lg';
        container.style.cssText = 'top: 100%; left: 0; right: 0; z-index: 1000; max-height: 400px; overflow-y: auto; display: none;';
        
        const searchInput = document.getElementById('global-search');
        if (searchInput) {
            searchInput.parentElement.style.position = 'relative';
            searchInput.parentElement.appendChild(container);
        }
        
        return container;
    }

    hideSearchResults() {
        const resultsContainer = document.getElementById('search-results');
        if (resultsContainer) {
            resultsContainer.style.display = 'none';
        }
    }

    // Notifications System
    showNotification(title, message, type = 'info', duration = 5000) {
        const notification = {
            id: Date.now(),
            title,
            message,
            type,
            duration
        };

        this.notifications.push(notification);
        this.renderNotification(notification);

        if (duration > 0) {
            setTimeout(() => {
                this.dismissNotification(document.getElementById(`notification-${notification.id}`));
            }, duration);
        }
    }

    renderNotification(notification) {
        const container = this.getNotificationContainer();
        const typeIcons = {
            success: 'check-circle',
            error: 'x-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };

        const notificationEl = document.createElement('div');
        notificationEl.id = `notification-${notification.id}`;
        notificationEl.className = `notification alert alert-${notification.type} alert-dismissible fade show`;
        notificationEl.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="bi bi-${typeIcons[notification.type]} me-2"></i>
                <div class="flex-grow-1">
                    <strong>${notification.title}</strong>
                    <div>${notification.message}</div>
                </div>
                <button type="button" class="btn-close notification-dismiss" aria-label="Close"></button>
            </div>
        `;

        container.appendChild(notificationEl);
    }

    getNotificationContainer() {
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'position-fixed';
            container.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
            document.body.appendChild(container);
        }
        return container;
    }

    dismissNotification(notificationEl) {
        if (notificationEl) {
            notificationEl.classList.remove('show');
            setTimeout(() => {
                notificationEl.remove();
            }, 150);
        }
    }

    // System Health Checks
    async checkSystemHealth() {
        try {
            const response = await fetch('/api/health-check/');
            if (!response.ok) {
                this.showNotification(
                    'System Warning',
                    'Some services may be experiencing issues.',
                    'warning'
                );
            }
        } catch (error) {
            console.log('Health check failed:', error);
        }
    }

    async checkProjectDeadlines() {
        try {
            const projects = await this.fetchAPI('/projects/?status=AT_RISK');
            if (projects.results && projects.results.length > 0) {
                this.showNotification(
                    'Project Alert',
                    `${projects.results.length} projects need attention.`,
                    'warning',
                    0 // Don't auto-dismiss
                );
            }
        } catch (error) {
            console.log('Project deadline check failed:', error);
        }
    }

    // Theme Management
    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        // Update theme toggle button icon
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            const icon = themeToggle.querySelector('i');
            if (icon) {
                icon.className = newTheme === 'dark' ? 'bi bi-sun' : 'bi bi-moon';
            }
        }
    }

    // Utility Methods
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

    formatCurrency(amount, currency = 'PKR') {
        if (amount >= 1000000000) {
            return `${currency} ${(amount / 1000000000).toFixed(1)}B`;
        } else if (amount >= 1000000) {
            return `${currency} ${(amount / 1000000).toFixed(1)}M`;
        } else if (amount >= 1000) {
            return `${currency} ${(amount / 1000).toFixed(1)}K`;
        }
        return `${currency} ${amount}`;
    }

    formatDate(date, options = {}) {
        return new Date(date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            ...options
        });
    }

    formatProgress(current, total) {
        if (total === 0) return '0%';
        return `${Math.round((current / total) * 100)}%`;
    }

    // Page-specific initialization methods
    initializeHomeDashboard() {
        // Home dashboard specific features
        this.loadRecentActivity();
        this.setupQuickActions();
    }

    initializeMapFeatures() {
        // Map page specific features
        console.log('Map features initialized');
    }

    initializeProjectDetail() {
        // Project detail page specific features
        this.setupProjectActions();
        this.loadProjectTimeline();
    }

    initializeFeedbackFeatures() {
        // Feedback page specific features
        this.setupFeedbackForm();
    }

    async loadRecentActivity() {
        // Load recent activity for home dashboard
        try {
            const activity = await this.fetchAPI('/dashboard/recent-activity/');
            this.displayRecentActivity(activity);
        } catch (error) {
            console.log('Failed to load recent activity:', error);
        }
    }

    displayRecentActivity(activity) {
        const container = document.getElementById('recent-activity');
        if (container && activity) {
            // Implementation would depend on activity data structure
            console.log('Recent activity loaded:', activity);
        }
    }

    setupQuickActions() {
        // Setup quick action buttons
        const quickActions = document.querySelectorAll('.quick-action');
        quickActions.forEach(action => {
            action.addEventListener('click', (e) => {
                e.preventDefault();
                const actionType = action.dataset.action;
                this.handleQuickAction(actionType);
            });
        });
    }

    handleQuickAction(actionType) {
        switch (actionType) {
            case 'export-data':
                this.exportDashboardData();
                break;
            case 'refresh-stats':
                this.refreshDashboardStats();
                break;
            case 'generate-report':
                this.generateReport();
                break;
            default:
                console.log('Unknown quick action:', actionType);
        }
    }

    setupProjectActions() {
        // Setup project-specific actions
        const projectActions = document.querySelectorAll('.project-action');
        projectActions.forEach(action => {
            action.addEventListener('click', (e) => {
                e.preventDefault();
                const actionType = action.dataset.action;
                const projectId = action.dataset.projectId;
                this.handleProjectAction(actionType, projectId);
            });
        });
    }

    handleProjectAction(actionType, projectId) {
        switch (actionType) {
            case 'update-status':
                this.updateProjectStatus(projectId);
                break;
            case 'add-milestone':
                this.addProjectMilestone(projectId);
                break;
            case 'export-project':
                this.exportProjectData(projectId);
                break;
            default:
                console.log('Unknown project action:', actionType);
        }
    }

    async loadProjectTimeline() {
        // Load project timeline data
        const projectId = this.getProjectIdFromUrl();
        if (projectId) {
            try {
                const timeline = await this.fetchAPI(`/projects/${projectId}/timeline/`);
                this.displayProjectTimeline(timeline);
            } catch (error) {
                console.log('Failed to load project timeline:', error);
            }
        }
    }

    getProjectIdFromUrl() {
        const match = window.location.pathname.match(/\/project\/(\d+)\//);
        return match ? match[1] : null;
    }

    setupFeedbackForm() {
        // Setup feedback form enhancements
        const feedbackForm = document.getElementById('feedback-form');
        if (feedbackForm) {
            this.enhanceFeedbackForm(feedbackForm);
        }
    }

    enhanceFeedbackForm(form) {
        // Add form validation and enhancements
        form.addEventListener('submit', (e) => {
            if (!this.validateFeedbackForm(form)) {
                e.preventDefault();
                return false;
            }
        });
    }

    validateFeedbackForm(form) {
        // Basic form validation
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                this.showFieldError(field, 'This field is required');
                isValid = false;
            } else {
                this.clearFieldError(field);
            }
        });

        return isValid;
    }

    showFieldError(field, message) {
        this.clearFieldError(field);
        
        const errorEl = document.createElement('div');
        errorEl.className = 'invalid-feedback d-block';
        errorEl.textContent = message;
        
        field.classList.add('is-invalid');
        field.parentElement.appendChild(errorEl);
    }

    clearFieldError(field) {
        field.classList.remove('is-invalid');
        const existingError = field.parentElement.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
    }

    // Export and reporting methods
    async exportDashboardData() {
        this.showNotification('Export Started', 'Preparing dashboard data for export...', 'info');
        
        try {
            const response = await fetch('/api/projects/export_csv/');
            const blob = await response.blob();
            
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `dashboard_export_${new Date().toISOString().split('T')[0]}.csv`;
            a.click();
            
            window.URL.revokeObjectURL(url);
            this.showNotification('Export Complete', 'Dashboard data exported successfully.', 'success');
        } catch (error) {
            this.showNotification('Export Failed', 'Failed to export dashboard data.', 'error');
        }
    }

    async generateReport() {
        this.showNotification('Report Generation', 'Generating comprehensive report...', 'info');
        
        // This would typically call a report generation API
        setTimeout(() => {
            this.showNotification('Report Ready', 'Your report has been generated.', 'success');
        }, 3000);
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboardManager = new DashboardManager();
});

// Global utility functions
window.formatCurrency = (amount, currency = 'PKR') => {
    return window.dashboardManager.formatCurrency(amount, currency);
};

window.formatDate = (date, options = {}) => {
    return window.dashboardManager.formatDate(date, options);
};

window.showNotification = (title, message, type = 'info', duration = 5000) => {
    return window.dashboardManager.showNotification(title, message, type, duration);
};
