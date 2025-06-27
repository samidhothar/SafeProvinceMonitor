"""
Management command to load dummy data for the Provincial Reform Portal.
"""
import random
from datetime import datetime, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from dashboard.models import (
    Sector, District, Contractor, Project, Procurement, KPIHistory, Feedback
)
from accounts.models import UserProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Load dummy data for the Provincial Reform Portal'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Loading dummy data...'))
        
        # Create superuser if not exists
        self.create_admin_user()
        
        # Create sectors
        self.create_sectors()
        
        # Create districts
        self.create_districts()
        
        # Create contractors
        self.create_contractors()
        
        # Create projects
        self.create_projects()
        
        # Create procurement records
        self.create_procurement_records()
        
        # Create KPI history
        self.create_kpi_history()
        
        # Create feedback
        self.create_feedback()
        
        self.stdout.write(self.style.SUCCESS('Dummy data loaded successfully!'))
    
    def create_admin_user(self):
        """Create admin user if not exists."""
        if not User.objects.filter(username='admin').exists():
            user = User.objects.create_superuser(
                username='admin',
                email='admin@reformportal.gov.pk',
                password='admin123',
                first_name='System',
                last_name='Administrator'
            )
            UserProfile.objects.create(
                user=user,
                role='ADMIN',
                department='IT Department',
                is_verified=True
            )
            self.stdout.write('Created admin user: admin/admin123')
    
    def create_sectors(self):
        """Create sector data."""
        sectors_data = [
            {'name': 'Education', 'icon': '🎓', 'color': '#0d6efd', 'description': 'Educational infrastructure and programs'},
            {'name': 'Healthcare', 'icon': '🏥', 'color': '#198754', 'description': 'Medical facilities and health services'},
            {'name': 'Transportation', 'icon': '🚗', 'color': '#ffc107', 'description': 'Roads, bridges, and transport infrastructure'},
            {'name': 'Water & Sanitation', 'icon': '💧', 'color': '#0dcaf0', 'description': 'Water supply and sanitation systems'},
            {'name': 'Energy', 'icon': '⚡', 'color': '#fd7e14', 'description': 'Power generation and distribution'},
            {'name': 'Agriculture', 'icon': '🌾', 'color': '#6f42c1', 'description': 'Agricultural development and support'},
        ]
        
        for sector_data in sectors_data:
            sector, created = Sector.objects.get_or_create(
                name=sector_data['name'],
                defaults=sector_data
            )
            if created:
                self.stdout.write(f'Created sector: {sector.name}')
    
    def create_districts(self):
        """Create district data."""
        districts_data = [
            {'name': 'Lahore', 'latitude': 31.5804, 'longitude': 74.3587, 'population': 11126285},
            {'name': 'Karachi', 'latitude': 24.8607, 'longitude': 67.0011, 'population': 14910352},
            {'name': 'Islamabad', 'latitude': 33.6844, 'longitude': 73.0479, 'population': 1014825},
            {'name': 'Rawalpindi', 'latitude': 33.5651, 'longitude': 73.0169, 'population': 2098231},
            {'name': 'Faisalabad', 'latitude': 31.4504, 'longitude': 73.1350, 'population': 3204726},
            {'name': 'Multan', 'latitude': 30.1575, 'longitude': 71.5249, 'population': 1871843},
            {'name': 'Peshawar', 'latitude': 34.0151, 'longitude': 71.5249, 'population': 1970042},
            {'name': 'Quetta', 'latitude': 30.1798, 'longitude': 66.9750, 'population': 1001205},
            {'name': 'Sialkot', 'latitude': 32.4945, 'longitude': 74.5229, 'population': 655852},
            {'name': 'Gujranwala', 'latitude': 32.1877, 'longitude': 74.1945, 'population': 2027001},
        ]
        
        for district_data in districts_data:
            district, created = District.objects.get_or_create(
                name=district_data['name'],
                defaults=district_data
            )
            if created:
                self.stdout.write(f'Created district: {district.name}')
    
    def create_contractors(self):
        """Create contractor data."""
        contractors_data = [
            {'name': 'Punjab Construction Co.', 'registration_number': 'PCC-001', 'rating': 4.5},
            {'name': 'Sindh Infrastructure Ltd.', 'registration_number': 'SIL-002', 'rating': 4.2},
            {'name': 'KPK Development Corp.', 'registration_number': 'KDC-003', 'rating': 4.0},
            {'name': 'Balochistan Builders', 'registration_number': 'BB-004', 'rating': 3.8},
            {'name': 'National Construction', 'registration_number': 'NC-005', 'rating': 4.7},
            {'name': 'Federal Works Agency', 'registration_number': 'FWA-006', 'rating': 4.3},
            {'name': 'Premier Engineering', 'registration_number': 'PE-007', 'rating': 4.1},
            {'name': 'Elite Infrastructure', 'registration_number': 'EI-008', 'rating': 4.4},
        ]
        
        for contractor_data in contractors_data:
            contractor_data.update({
                'contact_person': f'Director {contractor_data["name"].split()[0]}',
                'email': f'contact@{contractor_data["name"].lower().replace(" ", "").replace(".", "")}.com',
                'phone': f'+92-{random.randint(300, 399)}-{random.randint(1000000, 9999999)}',
                'address': f'{random.randint(1, 999)} Business District, {random.choice(["Lahore", "Karachi", "Islamabad"])}',
                'is_active': True,
                'completion_rate': random.uniform(75, 95)
            })
            
            contractor, created = Contractor.objects.get_or_create(
                registration_number=contractor_data['registration_number'],
                defaults=contractor_data
            )
            if created:
                self.stdout.write(f'Created contractor: {contractor.name}')
    
    def create_projects(self):
        """Create project data."""
        sectors = list(Sector.objects.all())
        districts = list(District.objects.all())
        contractors = list(Contractor.objects.all())
        statuses = ['COMPLETE', 'ON_TRACK', 'AT_RISK', 'DELAYED']
        
        projects_data = [
            'School Building Renovation',
            'Hospital Equipment Upgrade',
            'Road Construction Phase 1',
            'Water Treatment Plant',
            'Solar Power Installation',
            'Agricultural Training Center',
            'Bridge Construction',
            'Health Clinic Establishment',
            'IT Lab Setup',
            'Irrigation System Upgrade',
            'Community Center Building',
            'Emergency Response Unit',
            'Public Transport Enhancement',
            'Waste Management System',
            'Digital Literacy Program',
            'Rural Electrification',
            'Market Infrastructure',
            'Sports Complex Development',
            'Library Modernization',
            'Healthcare Equipment',
            'Road Maintenance',
            'Water Distribution Network',
            'Renewable Energy Project',
            'Skill Development Center',
            'Emergency Services Upgrade',
            'Educational Technology',
            'Public Safety Initiative',
            'Environmental Protection',
            'Infrastructure Modernization',
            'Community Development'
        ]
        
        admin_user = User.objects.filter(is_superuser=True).first()
        
        for i, project_name in enumerate(projects_data):
            sector = random.choice(sectors)
            district = random.choice(districts)
            contractor = random.choice(contractors)
            status = random.choice(statuses)
            
            # Generate realistic dates
            start_date = datetime.now().date() - timedelta(days=random.randint(30, 365))
            duration = random.randint(90, 730)  # 3 months to 2 years
            end_date_planned = start_date + timedelta(days=duration)
            
            # Set actual end date for completed projects
            end_date_actual = None
            if status == 'COMPLETE':
                end_date_actual = start_date + timedelta(days=random.randint(duration-30, duration+60))
            
            # Generate budget
            budget_allocated = Decimal(random.randint(500000, 50000000))
            budget_spent = budget_allocated * Decimal(random.uniform(0.1, 0.9))
            
            # Generate progress based on status
            if status == 'COMPLETE':
                progress = 100
            elif status == 'ON_TRACK':
                progress = random.randint(30, 80)
            elif status == 'AT_RISK':
                progress = random.randint(20, 60)
            else:  # DELAYED
                progress = random.randint(10, 50)
            
            # Generate KPI data
            kpi_target = random.randint(80, 100)
            kpi_achieved = random.randint(60, kpi_target)
            kpi_units = ['Percentage', 'Units', 'People Served', 'Kilometers', 'Facilities']
            
            project_data = {
                'name': f'{project_name} - {district.name}',
                'description': f'Implementation of {project_name.lower()} in {district.name} district to improve {sector.name.lower()} services.',
                'sector': sector,
                'district': district,
                'contractor': contractor,
                'status': status,
                'start_date': start_date,
                'end_date_planned': end_date_planned,
                'end_date_actual': end_date_actual,
                'progress_percentage': progress,
                'budget_allocated': budget_allocated,
                'budget_spent': budget_spent,
                'kpi_target': kpi_target,
                'kpi_achieved': kpi_achieved,
                'kpi_unit': random.choice(kpi_units),
                'latitude': district.latitude + random.uniform(-0.1, 0.1),
                'longitude': district.longitude + random.uniform(-0.1, 0.1),
                'created_by': admin_user
            }
            
            project, created = Project.objects.get_or_create(
                name=project_data['name'],
                defaults=project_data
            )
            if created:
                self.stdout.write(f'Created project: {project.name}')
    
    def create_procurement_records(self):
        """Create procurement records for projects."""
        projects = Project.objects.all()
        contractors = list(Contractor.objects.all())
        
        for project in projects:
            # Create 1-2 procurement records per project
            num_procurements = random.randint(1, 2)
            
            for i in range(num_procurements):
                tender_amount = project.budget_allocated * Decimal(random.uniform(0.8, 1.2))
                award_amount = tender_amount * Decimal(random.uniform(0.9, 1.1))
                
                procurement_data = {
                    'project': project,
                    'tender_id': f'TND-{project.id}-{i+1:02d}',
                    'tender_title': f'Tender for {project.name} - Phase {i+1}',
                    'tender_amount': tender_amount,
                    'award_amount': award_amount,
                    'contractor': random.choice(contractors),
                    'award_date': project.start_date + timedelta(days=random.randint(0, 30)),
                    'is_active': True
                }
                
                procurement, created = Procurement.objects.get_or_create(
                    tender_id=procurement_data['tender_id'],
                    defaults=procurement_data
                )
    
    def create_kpi_history(self):
        """Create KPI history for projects."""
        projects = Project.objects.all()
        admin_user = User.objects.filter(is_superuser=True).first()
        
        for project in projects:
            # Create 5-10 KPI records per project
            start_date = project.start_date
            end_date = project.end_date_actual or project.end_date_planned
            
            # Generate KPI records over time
            for i in range(5, 11):
                record_date = start_date + timedelta(days=i * 30)
                if record_date > end_date:
                    break
                
                # Gradually increasing KPI achievement
                base_achievement = (i / 10) * project.kpi_target
                kpi_achieved = min(project.kpi_target, base_achievement + random.randint(-5, 10))
                
                kpi_data = {
                    'project': project,
                    'date': record_date,
                    'kpi_achieved': kpi_achieved,
                    'notes': f'KPI update #{i} - Progress tracking',
                    'recorded_by': admin_user
                }
                
                KPIHistory.objects.get_or_create(
                    project=project,
                    date=record_date,
                    defaults=kpi_data
                )
    
    def create_feedback(self):
        """Create citizen feedback for projects."""
        projects = Project.objects.all()
        
        feedback_comments = [
            'Great progress on this project!',
            'The work quality is excellent.',
            'Some delays noticed but overall good.',
            'Happy with the improvements.',
            'Could be better managed.',
            'Excellent implementation.',
            'Minor issues with coordination.',
            'Very satisfied with results.',
            'Good work by the team.',
            'Some areas need improvement.'
        ]
        
        citizen_names = [
            'Ahmad Ali', 'Fatima Khan', 'Muhammad Hassan', 'Ayesha Malik',
            'Ali Raza', 'Zainab Ahmed', 'Usman Shah', 'Hina Butt',
            'Tariq Mahmood', 'Saira Batool'
        ]
        
        for project in projects:
            # Create 2-5 feedback records per project
            num_feedback = random.randint(2, 5)
            
            for i in range(num_feedback):
                feedback_data = {
                    'project': project,
                    'citizen_name': random.choice(citizen_names),
                    'citizen_email': f'citizen{random.randint(1, 100)}@example.com',
                    'rating': random.randint(3, 5),
                    'comment': random.choice(feedback_comments),
                    'is_verified': random.choice([True, False]),
                    'is_public': True,
                    'ip_address': f'192.168.1.{random.randint(1, 255)}',
                    'user_agent': 'Mozilla/5.0 (compatible; citizen feedback)'
                }
                
                Feedback.objects.create(**feedback_data)