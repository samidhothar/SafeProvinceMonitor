"""
Views for dashboard app - both API and template views.
"""
import csv
from datetime import date, timedelta
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Sum, Avg, Count, Case, When, Value, DecimalField
from django.db.models.functions import Coalesce
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from rest_framework import status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Sector, District, Contractor, Project, 
    Procurement, KPIHistory, Feedback
)
from .serializers import (
    SectorSerializer, DistrictSerializer, ContractorSerializer,
    ProjectListSerializer, ProjectDetailSerializer, ProjectCreateUpdateSerializer,
    ProcurementSerializer, KPIHistorySerializer, FeedbackSerializer,
    FinanceSummarySerializer, DashboardStatsSerializer
)


# Template Views
def home_view(request):
    """Home dashboard view."""
    # Get dashboard statistics
    stats = get_dashboard_stats()
    
    # Get recent projects
    recent_projects = Project.objects.select_related('sector', 'district').order_by('-created_at')[:5]
    
    # Get sector-wise stats
    sectors = Sector.objects.annotate(
        project_count=Count('projects'),
        total_budget=Coalesce(Sum('projects__budget_allocated'), Value(0, output_field=DecimalField())),
        total_spent=Coalesce(Sum('projects__budget_spent'), Value(0, output_field=DecimalField()))
    ).order_by('name')
    
    context = {
        'stats': stats,
        'recent_projects': recent_projects,
        'sectors': sectors,
    }
    return render(request, 'dashboard/home.html', context)


def map_view(request):
    """Interactive map view."""
    # Get projects with location data
    projects = Project.objects.select_related('sector', 'district').filter(
        latitude__isnull=False, 
        longitude__isnull=False
    )
    
    # Prepare map data
    map_data = []
    for project in projects:
        map_data.append({
            'id': project.id,
            'name': project.name,
            'sector': project.sector.name,
            'district': project.district.name,
            'status': project.status,
            'progress': float(project.progress_percentage),
            'budget_utilization': float(project.budget_utilization_percentage),
            'lat': float(project.latitude),
            'lng': float(project.longitude),
        })
    
    context = {
        'projects_json': map_data,
        'sectors': Sector.objects.all(),
        'districts': District.objects.all(),
    }
    return render(request, 'dashboard/map.html', context)


def project_detail_view(request, project_id):
    """Project detail view."""
    project = get_object_or_404(
        Project.objects.select_related('sector', 'district', 'contractor'),
        id=project_id
    )
    
    # Get KPI history for chart
    kpi_history = project.kpi_history.order_by('date')
    
    # Get feedback
    feedback = project.feedback.filter(is_public=True).order_by('-created_at')
    
    # Check if user can edit
    can_edit = False
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        can_edit = request.user.profile.can_edit_projects
    
    context = {
        'project': project,
        'kpi_history': kpi_history,
        'feedback': feedback,
        'can_edit': can_edit,
    }
    return render(request, 'dashboard/project_detail.html', context)


def procurement_view(request):
    """Procurement and contracts view."""
    procurements = Procurement.objects.select_related(
        'project', 'contractor'
    ).order_by('-award_date')
    
    # Pagination
    paginator = Paginator(procurements, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'procurements': page_obj.object_list,
    }
    return render(request, 'dashboard/procurement.html', context)


def feedback_view(request):
    """Public feedback view and form."""
    projects = Project.objects.select_related('sector', 'district').order_by('name')
    recent_feedback = Feedback.objects.filter(
        is_public=True
    ).select_related('project').order_by('-created_at')[:10]
    
    context = {
        'projects': projects,
        'recent_feedback': recent_feedback,
    }
    return render(request, 'dashboard/feedback.html', context)


# API Views
class ProjectViewSet(ModelViewSet):
    """ViewSet for Project CRUD operations."""
    queryset = Project.objects.select_related('sector', 'district', 'contractor')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['sector', 'district', 'status', 'contractor']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'start_date', 'progress_percentage']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'retrieve':
            return ProjectDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProjectCreateUpdateSerializer
        return ProjectListSerializer

    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """Set created_by when creating project."""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'])
    def kpi_history(self, request, pk=None):
        """Get KPI history for a project."""
        project = self.get_object()
        kpi_history = project.kpi_history.order_by('date')
        serializer = KPIHistorySerializer(kpi_history, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """Export projects to CSV."""
        projects = self.filter_queryset(self.get_queryset())
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="projects.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Name', 'Sector', 'District', 'Status', 'Progress %',
            'Budget Allocated', 'Budget Spent', 'Budget Utilization %',
            'KPI Target', 'KPI Achieved', 'KPI Achievement %',
            'Start Date', 'End Date Planned', 'Days Remaining'
        ])
        
        for project in projects:
            writer.writerow([
                project.id, project.name, project.sector.name, project.district.name,
                project.get_status_display(), project.progress_percentage,
                project.budget_allocated, project.budget_spent, project.budget_utilization_percentage,
                project.kpi_target, project.kpi_achieved, project.kpi_achievement_percentage,
                project.start_date, project.end_date_planned, project.days_remaining
            ])
        
        return response


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def finance_summary(request):
    """Get financial summary by sector and district."""
    # Summary by sector
    sector_summary = Sector.objects.annotate(
        total_allocated=Coalesce(Sum('projects__budget_allocated'), Value(0, output_field=DecimalField())),
        total_spent=Coalesce(Sum('projects__budget_spent'), Value(0, output_field=DecimalField())),
        project_count=Count('projects')
    ).values('name', 'total_allocated', 'total_spent', 'project_count')
    
    # Summary by district
    district_summary = District.objects.annotate(
        total_allocated=Coalesce(Sum('projects__budget_allocated'), Value(0, output_field=DecimalField())),
        total_spent=Coalesce(Sum('projects__budget_spent'), Value(0, output_field=DecimalField())),
        project_count=Count('projects')
    ).values('name', 'total_allocated', 'total_spent', 'project_count')
    
    # Calculate utilization percentages
    for summary in sector_summary:
        if summary['total_allocated'] > 0:
            summary['utilization_percentage'] = round(
                (summary['total_spent'] / summary['total_allocated']) * 100, 2
            )
        else:
            summary['utilization_percentage'] = 0
    
    for summary in district_summary:
        if summary['total_allocated'] > 0:
            summary['utilization_percentage'] = round(
                (summary['total_spent'] / summary['total_allocated']) * 100, 2
            )
        else:
            summary['utilization_percentage'] = 0
    
    return Response({
        'by_sector': list(sector_summary),
        'by_district': list(district_summary)
    })


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def submit_feedback(request):
    """Submit citizen feedback (public endpoint)."""
    serializer = FeedbackSerializer(data=request.data)
    if serializer.is_valid():
        # Get client IP and user agent
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        feedback = serializer.save(
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return Response(
            FeedbackSerializer(feedback).data,
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def dashboard_stats(request):
    """Get dashboard statistics."""
    stats = get_dashboard_stats()
    return Response(stats)


# Utility functions
def get_dashboard_stats():
    """Calculate dashboard statistics."""
    total_projects = Project.objects.count()
    completed_projects = Project.objects.filter(status='COMPLETE').count()
    delayed_projects = Project.objects.filter(status='DELAYED').count()
    at_risk_projects = Project.objects.filter(status='AT_RISK').count()
    
    # Financial stats
    financial_stats = Project.objects.aggregate(
        total_allocated=Coalesce(Sum('budget_allocated'), Value(0, output_field=DecimalField())),
        total_spent=Coalesce(Sum('budget_spent'), Value(0, output_field=DecimalField())),
        average_progress=Coalesce(Avg('progress_percentage'), Value(0, output_field=DecimalField()))
    )
    
    completion_percentage = 0
    if total_projects > 0:
        completion_percentage = round((completed_projects / total_projects) * 100, 2)
    
    return {
        'total_projects': total_projects,
        'completed_projects': completed_projects,
        'delayed_projects': delayed_projects,
        'at_risk_projects': at_risk_projects,
        'total_budget_allocated': financial_stats['total_allocated'],
        'total_budget_spent': financial_stats['total_spent'],
        'average_progress': round(financial_stats['average_progress'], 2),
        'completion_percentage': completion_percentage,
    }


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# Additional API endpoints
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def sectors_list(request):
    """List all sectors with project counts."""
    sectors = Sector.objects.annotate(
        project_count=Count('projects')
    )
    serializer = SectorSerializer(sectors, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def districts_list(request):
    """List all districts with project counts."""
    districts = District.objects.annotate(
        project_count=Count('projects')
    )
    serializer = DistrictSerializer(districts, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def contractors_list(request):
    """List all contractors."""
    contractors = Contractor.objects.filter(is_active=True)
    serializer = ContractorSerializer(contractors, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def project_feedback(request, project_id):
    """Get feedback for a specific project."""
    project = get_object_or_404(Project, id=project_id)
    feedback = project.feedback.filter(is_public=True).order_by('-created_at')
    serializer = FeedbackSerializer(feedback, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def map_data(request):
    """Get project data for map visualization."""
    projects = Project.objects.select_related('sector', 'district').filter(
        latitude__isnull=False,
        longitude__isnull=False
    )
    
    data = []
    for project in projects:
        data.append({
            'id': project.id,
            'name': project.name,
            'sector': project.sector.name,
            'sector_color': project.sector.color,
            'district': project.district.name,
            'status': project.status,
            'status_display': project.get_status_display(),
            'progress': float(project.progress_percentage),
            'budget_allocated': float(project.budget_allocated),
            'budget_spent': float(project.budget_spent),
            'budget_utilization': float(project.budget_utilization_percentage),
            'latitude': float(project.latitude),
            'longitude': float(project.longitude),
        })
    
    return Response(data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    """Health check endpoint for system monitoring."""
    try:
        # Basic database connectivity check
        Project.objects.count()
        return Response({
            'status': 'healthy',
            'timestamp': timezone.now(),
            'database': 'connected'
        })
    except Exception as e:
        return Response({
            'status': 'unhealthy',
            'timestamp': timezone.now(),
            'database': 'disconnected',
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def recent_activity(request):
    """Get recent activity for dashboard."""
    try:
        # Get recent projects (last 30 days)
        recent_projects = Project.objects.filter(
            created_at__gte=timezone.now() - timezone.timedelta(days=30)
        ).order_by('-created_at')[:10]
        
        # Get recent feedback (last 7 days)
        recent_feedback = Feedback.objects.filter(
            created_at__gte=timezone.now() - timezone.timedelta(days=7),
            is_public=True
        ).order_by('-created_at')[:5]
        
        activity_data = {
            'recent_projects': [
                {
                    'id': p.id,
                    'name': p.name,
                    'sector': p.sector.name,
                    'district': p.district.name,
                    'status': p.status,
                    'created_at': p.created_at
                }
                for p in recent_projects
            ],
            'recent_feedback': [
                {
                    'id': f.id,
                    'project_name': f.project.name,
                    'citizen_name': f.citizen_name,
                    'rating': f.rating,
                    'created_at': f.created_at
                }
                for f in recent_feedback
            ]
        }
        
        return Response(activity_data)
    except Exception as e:
        return Response({
            'error': 'Failed to load recent activity',
            'message': str(e)
        }, status=500)
