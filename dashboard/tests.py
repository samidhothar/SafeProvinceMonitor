"""
Unit tests for dashboard app.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from decimal import Decimal
from datetime import date, timedelta
from .models import (
    Sector, District, Contractor, Project, 
    Procurement, KPIHistory, Feedback
)
from accounts.models import UserProfile

User = get_user_model()


class ModelTests(TestCase):
    """Test cases for dashboard models."""
    
    def setUp(self):
        """Set up test data."""
        self.sector = Sector.objects.create(
            name='Health',
            icon='🏥',
            description='Healthcare projects'
        )
        self.district = District.objects.create(
            name='Lahore',
            latitude=31.5497,
            longitude=74.3436
        )
        self.contractor = Contractor.objects.create(
            name='ABC Construction',
            registration_number='REG001',
            contact_person='John Doe',
            phone='+92-300-1234567',
            email='contact@abc.com',
            address='123 Main St, Lahore',
            rating=4.5
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Hospital',
            description='Building a new hospital',
            sector=self.sector,
            district=self.district,
            contractor=self.contractor,
            start_date=date.today(),
            end_date_planned=date.today() + timedelta(days=365),
            budget_allocated=Decimal('10000000.00'),
            budget_spent=Decimal('2000000.00'),
            kpi_target=Decimal('100.00'),
            kpi_achieved=Decimal('20.00'),
            created_by=self.user
        )
    
    def test_sector_creation(self):
        """Test sector model creation."""
        self.assertEqual(self.sector.name, 'Health')
        self.assertEqual(self.sector.icon, '🏥')
        self.assertEqual(str(self.sector), 'Health')
    
    def test_district_creation(self):
        """Test district model creation."""
        self.assertEqual(self.district.name, 'Lahore')
        self.assertEqual(self.district.latitude, Decimal('31.5497'))
        self.assertEqual(str(self.district), 'Lahore')
    
    def test_contractor_creation(self):
        """Test contractor model creation."""
        self.assertEqual(self.contractor.name, 'ABC Construction')
        self.assertEqual(self.contractor.rating, Decimal('4.5'))
        self.assertEqual(self.contractor.completion_rate, 0)  # No completed projects yet
    
    def test_project_creation(self):
        """Test project model creation."""
        self.assertEqual(self.project.name, 'Test Hospital')
        self.assertEqual(self.project.sector, self.sector)
        self.assertEqual(self.project.district, self.district)
        self.assertEqual(self.project.budget_utilization_percentage, 20.0)
        self.assertEqual(self.project.kpi_achievement_percentage, 20.0)
    
    def test_project_properties(self):
        """Test project calculated properties."""
        self.assertGreater(self.project.days_remaining, 0)
        self.assertFalse(self.project.is_delayed)
        self.assertEqual(self.project.budget_utilization_percentage, 20.0)


class ProjectViewTests(TestCase):
    """Test cases for project views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.sector = Sector.objects.create(name='Health')
        self.district = District.objects.create(name='Lahore')
        self.project = Project.objects.create(
            name='Test Project',
            description='Test description',
            sector=self.sector,
            district=self.district,
            start_date=date.today(),
            end_date_planned=date.today() + timedelta(days=365),
            budget_allocated=Decimal('1000000.00'),
            kpi_target=Decimal('100.00')
        )
    
    def test_home_view(self):
        """Test home dashboard view."""
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')
    
    def test_map_view(self):
        """Test map view."""
        response = self.client.get(reverse('dashboard:map'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Map')
    
    def test_project_detail_view(self):
        """Test project detail view."""
        response = self.client.get(
            reverse('dashboard:project_detail', kwargs={'project_id': self.project.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.project.name)
    
    def test_feedback_view(self):
        """Test feedback view."""
        response = self.client.get(reverse('dashboard:feedback'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Feedback')


class ProjectAPITests(APITestCase):
    """Test cases for project API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        UserProfile.objects.create(user=self.user, role='ADMIN')
        self.token = Token.objects.create(user=self.user)
        
        self.sector = Sector.objects.create(name='Health')
        self.district = District.objects.create(name='Lahore')
        self.project = Project.objects.create(
            name='Test Project',
            description='Test description',
            sector=self.sector,
            district=self.district,
            start_date=date.today(),
            end_date_planned=date.today() + timedelta(days=365),
            budget_allocated=Decimal('1000000.00'),
            kpi_target=Decimal('100.00')
        )
    
    def test_project_list_api(self):
        """Test project list API endpoint."""
        url = reverse('dashboard:project-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_project_detail_api(self):
        """Test project detail API endpoint."""
        url = reverse('dashboard:project-detail', kwargs={'pk': self.project.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.project.name)
    
    def test_project_create_api_authenticated(self):
        """Test project creation via API (authenticated)."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = reverse('dashboard:project-list')
        data = {
            'name': 'New Project',
            'description': 'New project description',
            'sector': self.sector.id,
            'district': self.district.id,
            'start_date': date.today().isoformat(),
            'end_date_planned': (date.today() + timedelta(days=365)).isoformat(),
            'budget_allocated': '2000000.00',
            'kpi_target': '200.00',
            'status': 'ON_TRACK'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 2)
    
    def test_project_create_api_unauthenticated(self):
        """Test project creation via API (unauthenticated)."""
        url = reverse('dashboard:project-list')
        data = {
            'name': 'New Project',
            'description': 'New project description',
            'sector': self.sector.id,
            'district': self.district.id,
            'start_date': date.today().isoformat(),
            'end_date_planned': (date.today() + timedelta(days=365)).isoformat(),
            'budget_allocated': '2000000.00',
            'kpi_target': '200.00'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class FeedbackAPITests(APITestCase):
    """Test cases for feedback API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.sector = Sector.objects.create(name='Health')
        self.district = District.objects.create(name='Lahore')
        self.project = Project.objects.create(
            name='Test Project',
            description='Test description',
            sector=self.sector,
            district=self.district,
            start_date=date.today(),
            end_date_planned=date.today() + timedelta(days=365),
            budget_allocated=Decimal('1000000.00'),
            kpi_target=Decimal('100.00')
        )
    
    def test_submit_feedback_api(self):
        """Test feedback submission via API."""
        url = reverse('dashboard:api_submit_feedback')
        data = {
            'project': self.project.id,
            'citizen_name': 'John Citizen',
            'citizen_email': 'john@example.com',
            'rating': 4,
            'comment': 'Great project progress!'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Feedback.objects.count(), 1)
        
        feedback = Feedback.objects.first()
        self.assertEqual(feedback.citizen_name, 'John Citizen')
        self.assertEqual(feedback.rating, 4)


class DashboardStatsAPITests(APITestCase):
    """Test cases for dashboard stats API."""
    
    def setUp(self):
        """Set up test data."""
        self.sector = Sector.objects.create(name='Health')
        self.district = District.objects.create(name='Lahore')
        
        # Create projects with different statuses
        Project.objects.create(
            name='Completed Project',
            description='Test',
            sector=self.sector,
            district=self.district,
            start_date=date.today() - timedelta(days=365),
            end_date_planned=date.today() - timedelta(days=30),
            status='COMPLETE',
            budget_allocated=Decimal('1000000.00'),
            kpi_target=Decimal('100.00')
        )
        
        Project.objects.create(
            name='Delayed Project',
            description='Test',
            sector=self.sector,
            district=self.district,
            start_date=date.today() - timedelta(days=200),
            end_date_planned=date.today() - timedelta(days=50),
            status='DELAYED',
            budget_allocated=Decimal('2000000.00'),
            kpi_target=Decimal('200.00')
        )
    
    def test_dashboard_stats_api(self):
        """Test dashboard stats API endpoint."""
        url = reverse('dashboard:api_dashboard_stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        self.assertEqual(data['total_projects'], 2)
        self.assertEqual(data['completed_projects'], 1)
        self.assertEqual(data['delayed_projects'], 1)
        self.assertEqual(data['completion_percentage'], 50.0)


class ExportTests(APITestCase):
    """Test cases for data export functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.sector = Sector.objects.create(name='Health')
        self.district = District.objects.create(name='Lahore')
        self.project = Project.objects.create(
            name='Test Project',
            description='Test description',
            sector=self.sector,
            district=self.district,
            start_date=date.today(),
            end_date_planned=date.today() + timedelta(days=365),
            budget_allocated=Decimal('1000000.00'),
            kpi_target=Decimal('100.00')
        )
    
    def test_csv_export(self):
        """Test CSV export functionality."""
        url = reverse('dashboard:project-export-csv')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="projects.csv"', response['Content-Disposition'])
