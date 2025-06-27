"""
Serializers for dashboard app API endpoints.
"""
from rest_framework import serializers
from .models import (
    Sector, District, Contractor, Project, 
    Procurement, KPIHistory, Feedback
)


class SectorSerializer(serializers.ModelSerializer):
    """Serializer for Sector model."""
    project_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Sector
        fields = ['id', 'name', 'icon', 'description', 'color', 'project_count', 'created_at']
        read_only_fields = ['created_at']


class DistrictSerializer(serializers.ModelSerializer):
    """Serializer for District model."""
    project_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = District
        fields = [
            'id', 'name', 'latitude', 'longitude', 'population', 
            'area_sq_km', 'project_count', 'created_at'
        ]
        read_only_fields = ['created_at']


class ContractorSerializer(serializers.ModelSerializer):
    """Serializer for Contractor model."""
    completion_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = Contractor
        fields = [
            'id', 'name', 'registration_number', 'contact_person', 
            'phone', 'email', 'address', 'rating', 'total_projects', 
            'completed_projects', 'completion_rate', 'is_active', 'created_at'
        ]
        read_only_fields = ['created_at']


class ProcurementSerializer(serializers.ModelSerializer):
    """Serializer for Procurement model."""
    cost_overrun_percentage = serializers.ReadOnlyField()
    has_cost_overrun = serializers.ReadOnlyField()
    contractor_name = serializers.CharField(source='contractor.name', read_only=True)
    
    class Meta:
        model = Procurement
        fields = [
            'id', 'tender_id', 'tender_title', 'tender_amount', 'award_date',
            'award_amount', 'contractor', 'contractor_name', 'tender_document_url',
            'boq_document_url', 'contract_document_url', 'cost_overrun_percentage',
            'has_cost_overrun', 'is_active', 'notes', 'created_at'
        ]
        read_only_fields = ['created_at']


class KPIHistorySerializer(serializers.ModelSerializer):
    """Serializer for KPI History model."""
    recorded_by_name = serializers.CharField(source='recorded_by.username', read_only=True)
    
    class Meta:
        model = KPIHistory
        fields = [
            'id', 'date', 'kpi_achieved', 'notes', 'recorded_by', 
            'recorded_by_name', 'created_at'
        ]
        read_only_fields = ['created_at']


class FeedbackSerializer(serializers.ModelSerializer):
    """Serializer for Feedback model."""
    rating_display = serializers.CharField(source='get_rating_display', read_only=True)
    
    class Meta:
        model = Feedback
        fields = [
            'id', 'citizen_name', 'citizen_email', 'citizen_phone', 
            'rating', 'rating_display', 'comment', 'is_verified', 
            'is_public', 'created_at'
        ]
        read_only_fields = ['created_at', 'is_verified']


class ProjectListSerializer(serializers.ModelSerializer):
    """Serializer for Project list view."""
    sector_name = serializers.CharField(source='sector.name', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)
    contractor_name = serializers.CharField(source='contractor.name', read_only=True)
    budget_utilization_percentage = serializers.ReadOnlyField()
    kpi_achievement_percentage = serializers.ReadOnlyField()
    days_remaining = serializers.ReadOnlyField()
    should_be_at_risk = serializers.ReadOnlyField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'sector', 'sector_name', 'district', 'district_name',
            'contractor', 'contractor_name', 'status', 'progress_percentage',
            'start_date', 'end_date_planned', 'end_date_actual', 'days_remaining',
            'budget_allocated', 'budget_spent', 'budget_utilization_percentage',
            'kpi_target', 'kpi_achieved', 'kpi_achievement_percentage',
            'should_be_at_risk', 'last_updated', 'created_at'
        ]
        read_only_fields = ['created_at', 'last_updated']


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Serializer for Project detail view."""
    sector = SectorSerializer(read_only=True)
    district = DistrictSerializer(read_only=True)
    contractor = ContractorSerializer(read_only=True)
    procurements = ProcurementSerializer(many=True, read_only=True)
    kpi_history = KPIHistorySerializer(many=True, read_only=True)
    feedback = FeedbackSerializer(many=True, read_only=True)
    
    # Computed fields
    budget_utilization_percentage = serializers.ReadOnlyField()
    kpi_achievement_percentage = serializers.ReadOnlyField()
    days_remaining = serializers.ReadOnlyField()
    should_be_at_risk = serializers.ReadOnlyField()
    is_delayed = serializers.ReadOnlyField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'sector', 'district', 'contractor',
            'start_date', 'end_date_planned', 'end_date_actual', 'status',
            'progress_percentage', 'budget_allocated', 'budget_spent',
            'budget_utilization_percentage', 'kpi_target', 'kpi_achieved',
            'kpi_unit', 'kpi_achievement_percentage', 'latitude', 'longitude',
            'days_remaining', 'should_be_at_risk', 'is_delayed',
            'procurements', 'kpi_history', 'feedback', 'created_by',
            'last_updated', 'created_at'
        ]
        read_only_fields = ['created_at', 'last_updated']


class ProjectCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating projects."""
    
    class Meta:
        model = Project
        fields = [
            'name', 'description', 'sector', 'district', 'contractor',
            'start_date', 'end_date_planned', 'end_date_actual', 'status',
            'progress_percentage', 'budget_allocated', 'budget_spent',
            'kpi_target', 'kpi_achieved', 'kpi_unit', 'latitude', 'longitude'
        ]

    def validate(self, data):
        """Validate project data."""
        if data.get('start_date') and data.get('end_date_planned'):
            if data['start_date'] >= data['end_date_planned']:
                raise serializers.ValidationError(
                    "End date must be after start date."
                )
        
        if data.get('budget_spent', 0) > data.get('budget_allocated', 0):
            raise serializers.ValidationError(
                "Budget spent cannot exceed budget allocated."
            )
        
        if data.get('kpi_achieved', 0) > data.get('kpi_target', 0):
            # Warning, not error - sometimes targets are exceeded
            pass
        
        return data


class FinanceSummarySerializer(serializers.Serializer):
    """Serializer for finance summary data."""
    sector_name = serializers.CharField()
    district_name = serializers.CharField()
    total_allocated = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_spent = serializers.DecimalField(max_digits=15, decimal_places=2)
    utilization_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    project_count = serializers.IntegerField()


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics."""
    total_projects = serializers.IntegerField()
    completed_projects = serializers.IntegerField()
    delayed_projects = serializers.IntegerField()
    at_risk_projects = serializers.IntegerField()
    total_budget_allocated = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_budget_spent = serializers.DecimalField(max_digits=15, decimal_places=2)
    average_progress = serializers.DecimalField(max_digits=5, decimal_places=2)
    completion_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
