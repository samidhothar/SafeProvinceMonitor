"""
Core models for the provincial reform monitoring portal.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

User = get_user_model()


class Sector(models.Model):
    """Sector model for categorizing projects."""
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, default='📊')  # Emoji or icon class
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=7, default='#007bff')  # Hex color code
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class District(models.Model):
    """District model for geographical categorization."""
    name = models.CharField(max_length=100, unique=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    population = models.IntegerField(null=True, blank=True)
    area_sq_km = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Contractor(models.Model):
    """Contractor model for project execution."""
    name = models.CharField(max_length=200)
    registration_number = models.CharField(max_length=100, unique=True)
    contact_person = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        default=0.0
    )
    total_projects = models.IntegerField(default=0)
    completed_projects = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def completion_rate(self):
        """Calculate completion rate percentage."""
        if self.total_projects == 0:
            return 0
        return round((self.completed_projects / self.total_projects) * 100, 2)

    class Meta:
        ordering = ['-rating', 'name']


class Project(models.Model):
    """Main project model."""
    
    STATUS_CHOICES = [
        ('ON_TRACK', 'On Track'),
        ('AT_RISK', 'At Risk'),
        ('DELAYED', 'Delayed'),
        ('COMPLETE', 'Complete'),
    ]

    # Basic Information
    name = models.CharField(max_length=300)
    description = models.TextField()
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, related_name='projects')
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='projects')
    contractor = models.ForeignKey(Contractor, on_delete=models.SET_NULL, null=True, blank=True, related_name='projects')

    # Timeline
    start_date = models.DateField()
    end_date_planned = models.DateField()
    end_date_actual = models.DateField(null=True, blank=True)
    
    # Status and Progress
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ON_TRACK')
    progress_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    
    # Financial
    budget_allocated = models.DecimalField(max_digits=15, decimal_places=2)
    budget_spent = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    
    # KPIs
    kpi_target = models.DecimalField(max_digits=10, decimal_places=2)
    kpi_achieved = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    kpi_unit = models.CharField(max_length=50, default='units')
    
    # Location
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.district.name}"

    @property
    def budget_utilization_percentage(self):
        """Calculate budget utilization percentage."""
        if self.budget_allocated == 0:
            return 0
        return round((self.budget_spent / self.budget_allocated) * 100, 2)

    @property
    def kpi_achievement_percentage(self):
        """Calculate KPI achievement percentage."""
        if self.kpi_target == 0:
            return 0
        return round((self.kpi_achieved / self.kpi_target) * 100, 2)

    @property
    def is_delayed(self):
        """Check if project is delayed based on current date."""
        from datetime import date
        return date.today() > self.end_date_planned and self.status != 'COMPLETE'

    @property
    def days_remaining(self):
        """Calculate days remaining until planned end date."""
        from datetime import date
        if self.status == 'COMPLETE':
            return 0
        delta = self.end_date_planned - date.today()
        return max(0, delta.days)

    @property
    def should_be_at_risk(self):
        """Determine if project should be flagged as at risk."""
        # Auto-predict delay if KPI achieved < 60% and >50% duration elapsed
        from datetime import date
        total_duration = (self.end_date_planned - self.start_date).days
        elapsed_duration = (date.today() - self.start_date).days
        
        if total_duration > 0:
            duration_percentage = (elapsed_duration / total_duration) * 100
            return (duration_percentage > 50 and 
                    self.kpi_achievement_percentage < 60 and 
                    self.status not in ['COMPLETE', 'DELAYED'])
        return False

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sector', 'district']),
            models.Index(fields=['status']),
            models.Index(fields=['start_date', 'end_date_planned']),
        ]


class Procurement(models.Model):
    """Procurement and tender information."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='procurements')
    tender_id = models.CharField(max_length=100, unique=True)
    tender_title = models.CharField(max_length=300)
    tender_amount = models.DecimalField(max_digits=15, decimal_places=2)
    award_date = models.DateField()
    award_amount = models.DecimalField(max_digits=15, decimal_places=2)
    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE)
    
    # Documents
    tender_document_url = models.URLField(blank=True, null=True)
    boq_document_url = models.URLField(blank=True, null=True)  # Bill of Quantities
    contract_document_url = models.URLField(blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tender_id} - {self.project.name}"

    @property
    def cost_overrun_percentage(self):
        """Calculate cost overrun percentage."""
        if self.tender_amount == 0:
            return 0
        return round(((self.award_amount - self.tender_amount) / self.tender_amount) * 100, 2)

    @property
    def has_cost_overrun(self):
        """Check if there's a cost overrun."""
        return self.award_amount > self.tender_amount

    class Meta:
        ordering = ['-award_date']


class KPIHistory(models.Model):
    """Historical KPI tracking for projects."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='kpi_history')
    date = models.DateField()
    kpi_achieved = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project.name} - {self.date} - {self.kpi_achieved}"

    class Meta:
        ordering = ['-date']
        unique_together = ['project', 'date']
        verbose_name = 'KPI History'
        verbose_name_plural = 'KPI Histories'


class Feedback(models.Model):
    """Citizen feedback for projects."""
    
    RATING_CHOICES = [
        (1, 'Very Poor'),
        (2, 'Poor'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='feedback')
    citizen_name = models.CharField(max_length=200)
    citizen_email = models.EmailField(blank=True, null=True)
    citizen_phone = models.CharField(max_length=20, blank=True, null=True)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    is_verified = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.citizen_name} - {self.project.name} - {self.rating}/5"

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'rating']),
            models.Index(fields=['is_verified', 'is_public']),
        ]
