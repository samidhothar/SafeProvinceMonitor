# Provincial Reform Portal - "Saaf | Sasta | Safe"

## Overview

This is a Django-based government transparency and accountability platform designed to monitor provincial reform projects. The system provides real-time tracking of government projects, procurement transparency, citizen feedback mechanisms, and data-driven insights through interactive dashboards and maps.

The portal serves multiple stakeholders including administrators, department heads, district officers, and the general public, each with appropriate access levels and functionality.

## System Architecture

### Backend Architecture
- **Framework**: Django 4.2 with Django REST Framework
- **Database**: PostgreSQL (configured via environment, with SQLite fallback for development)
- **Authentication**: Django's built-in authentication system with role-based permissions
- **API Design**: RESTful API endpoints with proper serialization
- **File Storage**: Local file storage for media files (avatars, documents)

### Frontend Architecture
- **Template Engine**: Django templates with Bootstrap 5 for responsive design
- **JavaScript**: Vanilla JavaScript with Chart.js for data visualization
- **Mapping**: Leaflet.js for interactive project mapping
- **CSS Framework**: Bootstrap 5 with custom CSS for styling
- **Icons**: Bootstrap Icons for consistent iconography

### Database Design
The system uses a relational model with the following key entities:
- **Projects**: Central entity linking sectors, districts, contractors, and timelines
- **User Management**: Extended user model with role-based profiles
- **Geographical Data**: District-based project categorization with coordinates
- **Financial Tracking**: Budget allocation and expenditure monitoring
- **Feedback System**: Citizen engagement and project feedback

## Key Components

### Applications
1. **Dashboard App**: Core functionality for project management, visualization, and reporting
2. **Accounts App**: User authentication, role management, and profile handling

### Models Structure
- **Project Management**: Sector, District, Project, Contractor models
- **Financial Tracking**: Procurement model for contract transparency
- **Performance Monitoring**: KPIHistory for tracking project progress over time
- **Citizen Engagement**: Feedback model for public input
- **User Management**: Extended User and UserProfile models

### API Endpoints
- **Project CRUD**: Full project lifecycle management
- **Financial Reports**: Budget vs expenditure analysis
- **Map Data**: Geographical project visualization
- **Feedback System**: Public feedback submission
- **Dashboard Statistics**: Real-time KPI aggregation

### User Roles
- **Admin**: Full system access and management
- **Department Head**: Departmental project oversight
- **District Officer**: Local project management
- **Public**: View projects and submit feedback

## Data Flow

### Project Lifecycle
1. Project creation with sector, district, and budget assignment
2. Contractor assignment through procurement process
3. Real-time KPI tracking and status updates
4. Citizen feedback collection and integration
5. Financial monitoring and transparency reporting

### Authentication Flow
1. User registration with role assignment
2. Profile verification by administrators
3. Role-based access control to features
4. API token-based authentication for mobile/external access

### Data Visualization Pipeline
1. Raw project data aggregation from database
2. KPI calculation and historical tracking
3. Geographical mapping with status indicators
4. Chart generation for dashboard displays
5. Export functionality for transparency reports

## External Dependencies

### Python Packages
- **Django 4.2**: Core web framework
- **Django REST Framework**: API development
- **Pillow**: Image processing for user avatars
- **psycopg2-binary**: PostgreSQL database adapter
- **django-cors-headers**: CORS handling for API access
- **django-filter**: Advanced filtering capabilities
- **dj-database-url**: Database configuration from environment

### Frontend Libraries
- **Bootstrap 5**: Responsive CSS framework
- **Chart.js**: Data visualization and charting
- **Leaflet.js**: Interactive mapping functionality
- **Bootstrap Icons**: Icon library

### Development Tools
- **Replit Environment**: PostgreSQL 16 and Python 3.11
- **UV Package Manager**: Dependency management
- **Django Management Commands**: Data loading and maintenance

## Deployment Strategy

### Environment Configuration
- Environment-based settings for database and security
- Debug mode controlled via environment variables
- Static file serving configured for production
- Media file handling for user uploads

### Database Setup
- Automated migrations on deployment
- Dummy data loading through management commands
- KPI update simulations for demonstration

### Production Considerations
- Secret key management through environment variables
- CORS configuration for API access
- Static file collection and serving
- Database connection pooling ready

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes

Recent Changes:
- June 27, 2025: Complete Django application setup and deployment
  - Fixed static file URL configuration issues in templates
  - Added missing API endpoints (health-check, recent-activity)
  - Resolved Django server startup issues with migrations and models
  - Created sample data (3 sectors, districts, projects) for demonstration
  - All functionality now working: dashboard, maps, procurement, feedback
  - Application successfully running on port 5000 with PostgreSQL database

## Changelog

Changelog:
- June 27, 2025: Provincial Reform Portal fully operational with working dashboard, API endpoints, and sample data