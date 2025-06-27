"""
URL configuration for dashboard app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for API endpoints
router = DefaultRouter()
router.register(r'projects', views.ProjectViewSet)

app_name = 'dashboard'

urlpatterns = [
    # Template views
    path('', views.home_view, name='home'),
    path('map/', views.map_view, name='map'),
    path('project/<int:project_id>/', views.project_detail_view, name='project_detail'),
    path('procurement/', views.procurement_view, name='procurement'),
    path('feedback/', views.feedback_view, name='feedback'),
    
    # API endpoints
    path('api/', include(router.urls)),
    path('api/finance/summary/', views.finance_summary, name='api_finance_summary'),
    path('api/feedback/', views.submit_feedback, name='api_submit_feedback'),
    path('api/dashboard/stats/', views.dashboard_stats, name='api_dashboard_stats'),
    path('api/sectors/', views.sectors_list, name='api_sectors'),
    path('api/districts/', views.districts_list, name='api_districts'),
    path('api/contractors/', views.contractors_list, name='api_contractors'),
    path('api/projects/<int:project_id>/feedback/', views.project_feedback, name='api_project_feedback'),
    path('api/map-data/', views.map_data, name='api_map_data'),
]
