"""
Admin configuration for dashboard app.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Sector, District, Contractor, Project, 
    Procurement, KPIHistory, Feedback
)


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    """Admin interface for Sector model."""
    list_display = ('name', 'icon', 'color', 'project_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    readonly_fields = ('created_at',)

    def project_count(self, obj):
        """Count of projects in this sector."""
        return obj.projects.count()
    project_count.short_description = 'Projects'


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    """Admin interface for District model."""
    list_display = ('name', 'latitude', 'longitude', 'population', 'project_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name',)
    readonly_fields = ('created_at',)

    def project_count(self, obj):
        """Count of projects in this district."""
        return obj.projects.count()
    project_count.short_description = 'Projects'


@admin.register(Contractor)
class ContractorAdmin(admin.ModelAdmin):
    """Admin interface for Contractor model."""
    list_display = ('name', 'registration_number', 'rating', 'completion_rate_display', 'is_active', 'created_at')
    list_filter = ('is_active', 'rating', 'created_at')
    search_fields = ('name', 'registration_number', 'contact_person', 'email')
    readonly_fields = ('created_at', 'completion_rate')

    def completion_rate_display(self, obj):
        """Display completion rate with color coding."""
        rate = obj.completion_rate
        if rate >= 80:
            color = 'green'
        elif rate >= 60:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, rate
        )
    completion_rate_display.short_description = 'Completion Rate'


class ProcurementInline(admin.TabularInline):
    """Inline admin for procurement."""
    model = Procurement
    extra = 0
    readonly_fields = ('cost_overrun_percentage',)


class KPIHistoryInline(admin.TabularInline):
    """Inline admin for KPI history."""
    model = KPIHistory
    extra = 0
    readonly_fields = ('created_at',)


class FeedbackInline(admin.TabularInline):
    """Inline admin for feedback."""
    model = Feedback
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin interface for Project model."""
    list_display = (
        'name', 'sector', 'district', 'status_display', 'progress_percentage', 
        'budget_utilization_display', 'kpi_achievement_display', 'created_at'
    )
    list_filter = ('status', 'sector', 'district', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = (
        'budget_utilization_percentage', 'kpi_achievement_percentage', 
        'days_remaining', 'should_be_at_risk', 'created_at', 'last_updated'
    )
    inlines = [ProcurementInline, KPIHistoryInline, FeedbackInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'sector', 'district', 'contractor')
        }),
        ('Timeline', {
            'fields': ('start_date', 'end_date_planned', 'end_date_actual', 'days_remaining')
        }),
        ('Status & Progress', {
            'fields': ('status', 'progress_percentage', 'should_be_at_risk')
        }),
        ('Financial', {
            'fields': ('budget_allocated', 'budget_spent', 'budget_utilization_percentage')
        }),
        ('KPIs', {
            'fields': ('kpi_target', 'kpi_achieved', 'kpi_unit', 'kpi_achievement_percentage')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'last_updated'),
            'classes': ('collapse',)
        })
    )

    def status_display(self, obj):
        """Display status with color coding."""
        status_colors = {
            'ON_TRACK': 'green',
            'AT_RISK': 'orange',
            'DELAYED': 'red',
            'COMPLETE': 'blue'
        }
        color = status_colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Status'

    def budget_utilization_display(self, obj):
        """Display budget utilization with color coding."""
        util = obj.budget_utilization_percentage
        if util > 100:
            color = 'red'
        elif util > 80:
            color = 'orange'
        else:
            color = 'green'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, util
        )
    budget_utilization_display.short_description = 'Budget Utilization'

    def kpi_achievement_display(self, obj):
        """Display KPI achievement with color coding."""
        achievement = obj.kpi_achievement_percentage
        if achievement >= 80:
            color = 'green'
        elif achievement >= 60:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, achievement
        )
    kpi_achievement_display.short_description = 'KPI Achievement'


@admin.register(Procurement)
class ProcurementAdmin(admin.ModelAdmin):
    """Admin interface for Procurement model."""
    list_display = (
        'tender_id', 'project', 'contractor', 'tender_amount', 
        'award_amount', 'cost_overrun_display', 'award_date'
    )
    list_filter = ('award_date', 'contractor', 'is_active')
    search_fields = ('tender_id', 'tender_title', 'project__name')
    readonly_fields = ('cost_overrun_percentage', 'has_cost_overrun', 'created_at')

    def cost_overrun_display(self, obj):
        """Display cost overrun with color coding."""
        overrun = obj.cost_overrun_percentage
        if overrun > 10:
            color = 'red'
        elif overrun > 0:
            color = 'orange'
        else:
            color = 'green'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, overrun
        )
    cost_overrun_display.short_description = 'Cost Overrun'


@admin.register(KPIHistory)
class KPIHistoryAdmin(admin.ModelAdmin):
    """Admin interface for KPI History model."""
    list_display = ('project', 'date', 'kpi_achieved', 'recorded_by', 'created_at')
    list_filter = ('date', 'project__sector', 'project__district')
    search_fields = ('project__name', 'notes')
    readonly_fields = ('created_at',)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    """Admin interface for Feedback model."""
    list_display = (
        'project', 'citizen_name', 'rating_display', 'is_verified', 
        'is_public', 'created_at'
    )
    list_filter = ('rating', 'is_verified', 'is_public', 'created_at')
    search_fields = ('citizen_name', 'citizen_email', 'project__name', 'comment')
    readonly_fields = ('ip_address', 'user_agent', 'created_at')
    
    actions = ['make_verified', 'make_unverified', 'make_public', 'make_private']

    def rating_display(self, obj):
        """Display rating with stars."""
        stars = '⭐' * obj.rating
        return f"{stars} ({obj.rating}/5)"
    rating_display.short_description = 'Rating'

    def make_verified(self, request, queryset):
        """Mark feedback as verified."""
        queryset.update(is_verified=True)
    make_verified.short_description = "Mark selected feedback as verified"

    def make_unverified(self, request, queryset):
        """Mark feedback as unverified."""
        queryset.update(is_verified=False)
    make_unverified.short_description = "Mark selected feedback as unverified"

    def make_public(self, request, queryset):
        """Mark feedback as public."""
        queryset.update(is_public=True)
    make_public.short_description = "Mark selected feedback as public"

    def make_private(self, request, queryset):
        """Mark feedback as private."""
        queryset.update(is_public=False)
    make_private.short_description = "Mark selected feedback as private"
