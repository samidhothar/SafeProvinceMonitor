"""
User authentication and profile models for the reform portal.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Extended user model with additional fields."""
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'auth_user_extended'


class UserProfile(models.Model):
    """User profile with role-based permissions."""
    
    ROLE_CHOICES = [
        ('ADMIN', 'Administrator'),
        ('DEPT_HEAD', 'Department Head'),
        ('DISTRICT_OFFICER', 'District Officer'),
        ('PUBLIC', 'Public User'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='PUBLIC')
    department = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    @property
    def is_admin(self):
        return self.role == 'ADMIN'

    @property
    def is_dept_head(self):
        return self.role == 'DEPT_HEAD'

    @property
    def is_district_officer(self):
        return self.role == 'DISTRICT_OFFICER'

    @property
    def is_public(self):
        return self.role == 'PUBLIC'

    @property
    def can_edit_projects(self):
        """Check if user can edit projects."""
        return self.role in ['ADMIN', 'DEPT_HEAD', 'DISTRICT_OFFICER']

    @property
    def can_view_financial_data(self):
        """Check if user can view detailed financial information."""
        return self.role in ['ADMIN', 'DEPT_HEAD']

    class Meta:
        db_table = 'accounts_userprofile'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
