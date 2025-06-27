"""
Management command to load dummy data for the reform portal.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
import random

from dashboard.models import (
    Sector, District, Contractor, Project, 
    Procurement, KPIHistory, Feedback
)
from accounts.models import UserProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Load dummy data for the provincial reform monitoring portal'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before loading dummy data',
        )

    def handle(self, *args, **options):
        """Execute the command."""
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            self.clear_data()

        self.stdout.write('Loading dummy data...')
        
        # Create users and profiles
        self.create_users()
        
        # Create sectors
        self.create_sectors()
        
        # Create districts
        self.create_districts()
        
        # Create contractors
        self.create_contractors()
        
        # Create projects
        self.create_projects()
        
        # Create procurement data
        self.create_procurement_data()
        
        # Create KPI history
        self.create_kpi_history()
        
        # Create feedback
        self.create_feedback()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully loaded dummy data!')
        )

    def clear_data(self):
        """Clear existing data."""
        models_to_clear = [
            Feedback, KPIHistory, Procurement, Project, 
            Contractor, District, Sector
        ]
        
        for model in models_to_clear:
            count = model.objects.count()
            model.objects.all().delete()
            self.stdout.write(f'Deleted {count} {model.__name__} records')

    def create_users(self):
        """Create dummy users with different roles."""
        users_data = [
            {'username': 'admin', 'email': 'admin@reform.gov.pk', 'role': 'ADMIN', 'first_name': 'System', 'last_name': 'Administrator'},
            {'username': 'health_dept', 'email': 'health@reform.gov.pk', 'role': 'DEPT_HEAD', 'first_name': 'Dr. Sarah', 'last_name': 'Ahmed', 'department': 'Health'},
            {'username': 'education_dept', 'email': 'education@reform.gov.pk', 'role': 'DEPT_HEAD', 'first_name': 'Prof. Ali', 'last_name': 'Khan', 'department': 'Education'},
            {'username': 'lahore_officer', 'email': 'lahore@reform.gov.pk', 'role': 'DISTRICT_OFFICER', 'first_name': 'Muhammad', 'last_name': 'Hassan', 'district': 'Lahore'},
            {'username': 'karachi_officer', 'email': 'karachi@reform.gov.pk', 'role': 'DISTRICT_OFFICER', 'first_name': 'Fatima', 'last_name': 'Sheikh', 'district': 'Karachi'},
        ]
        
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'is_staff': user_data['role'] == 'ADMIN',
                    'is_superuser': user_data['role'] == 'ADMIN',
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()
            
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'role': user_data['role'],
                    'department': user_data.get('department', ''),
                    'district': user_data.get('district', ''),
                    'is_verified': True,
                }
            )
            
            if created:
                self.stdout.write(f'Created user: {user.username} ({user_data["role"]})')

    def create_sectors(self):
        """Create sectors."""
        sectors_data = [
            {'name': 'Water & Sanitation', 'icon': '💧', 'color': '#2196F3', 'description': 'Water supply, drainage, and sanitation projects'},
            {'name': 'Health', 'icon': '🏥', 'color': '#F44336', 'description': 'Healthcare infrastructure and services'},
            {'name': 'Education', 'icon': '🎓', 'color': '#4CAF50', 'description': 'School infrastructure and education technology'},
            {'name': 'Electricity', 'icon': '⚡', 'color': '#FF9800', 'description': 'Power generation and distribution projects'},
            {'name': 'Transport', 'icon': '🚗', 'color': '#9C27B0', 'description': 'Roads, bridges, and public transport'},
            {'name': 'Security', 'icon': '🛡️', 'color': '#607D8B', 'description': 'Law enforcement and public safety'},
        ]
        
        for sector_data in sectors_data:
            sector, created = Sector.objects.get_or_create(
                name=sector_data['name'],
                defaults=sector_data
            )
            if created:
                self.stdout.write(f'Created sector: {sector.name}')

    def create_districts(self):
        """Create districts with coordinates."""
        districts_data = [
            {'name': 'Lahore', 'latitude': 31.5497, 'longitude': 74.3436, 'population': 11126285},
            {'name': 'Karachi', 'latitude': 24.8607, 'longitude': 67.0011, 'population': 14910352},
            {'name': 'Faisalabad', 'latitude': 31.4504, 'longitude': 73.1350, 'population': 3204726},
            {'name': 'Rawalpindi', 'latitude': 33.5651, 'longitude': 73.0169, 'population': 2098231},
            {'name': 'Multan', 'latitude': 30.1575, 'longitude': 71.5249, 'population': 1871843},
            {'name': 'Peshawar', 'latitude': 34.0151, 'longitude': 71.5249, 'population': 1970042},
            {'name': 'Quetta', 'latitude': 30.1798, 'longitude': 66.9750, 'population': 1001205},
            {'name': 'Islamabad', 'latitude': 33.6844, 'longitude': 73.0479, 'population': 1014825},
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
        """Create contractors."""
        contractors_data = [
            {
                'name': 'National Construction Company',
                'registration_number': 'NCC-001',
                'contact_person': 'Ahmad Ali',
                'phone': '+92-42-35741234',
                'email': 'info@ncc.com.pk',
                'address': 'Plot 15, Industrial Area, Lahore',
                'rating': 4.2,
                'total_projects': 25,
                'completed_projects': 20,
            },
            {
                'name': 'Frontier Works Organization',
                'registration_number': 'FWO-002',
                'contact_person': 'Col. Tariq Mahmood',
                'phone': '+92-51-90785555',
                'email': 'contracts@fwo.com.pk',
                'address': 'FWO House, Rawalpindi',
                'rating': 4.8,
                'total_projects': 45,
                'completed_projects': 42,
            },
            {
                'name': 'Descon Engineering',
                'registration_number': 'DES-003',
                'contact_person': 'Engr. Saima Khan',
                'phone': '+92-42-35871000',
                'email': 'projects@descon.com',
                'address': '18-Kot Lakhpat Industrial Estate, Lahore',
                'rating': 4.1,
                'total_projects': 30,
                'completed_projects': 24,
            },
            {
                'name': 'Habib Construction Services',
                'registration_number': 'HCS-004',
                'contact_person': 'Muhammad Habib',
                'phone': '+92-21-35682000',
                'email': 'info@habibconstruction.pk',
                'address': 'Plot 25, SITE Industrial Area, Karachi',
                'rating': 3.9,
                'total_projects': 20,
                'completed_projects': 16,
            },
            {
                'name': 'China State Construction Engineering Corporation',
                'registration_number': 'CSC-005',
                'contact_person': 'Li Wei',
                'phone': '+92-51-28752000',
                'email': 'pakistan@cscec.com',
                'address': 'Diplomatic Enclave, Islamabad',
                'rating': 4.5,
                'total_projects': 15,
                'completed_projects': 12,
            },
        ]
        
        for contractor_data in contractors_data:
            contractor, created = Contractor.objects.get_or_create(
                registration_number=contractor_data['registration_number'],
                defaults=contractor_data
            )
            if created:
                self.stdout.write(f'Created contractor: {contractor.name}')

    def create_projects(self):
        """Create 30 projects across sectors and districts."""
        sectors = list(Sector.objects.all())
        districts = list(District.objects.all())
        contractors = list(Contractor.objects.all())
        admin_user = User.objects.filter(username='admin').first()
        
        projects_data = [
            # Water & Sanitation Projects
            {
                'name': 'Canal Lining Project - Lahore-Faisalabad',
                'description': 'Lining of main canal to reduce water losses by 25% and improve irrigation efficiency',
                'sector': 'Water & Sanitation',
                'districts': ['Lahore', 'Faisalabad'],
                'budget': 15000000000,
                'kpi_target': 100,
                'kpi_unit': 'km of canal lined',
                'duration_days': 790,
            },
            {
                'name': 'Urban Drainage System - Karachi',
                'description': 'Construction of modern drainage system to prevent urban flooding',
                'sector': 'Water & Sanitation',
                'districts': ['Karachi'],
                'budget': 8500000000,
                'kpi_target': 150,
                'kpi_unit': 'km of drainage',
                'duration_days': 600,
            },
            {
                'name': 'Water Treatment Plant - Rawalpindi',
                'description': 'Installation of advanced water treatment facility for clean drinking water',
                'sector': 'Water & Sanitation',
                'districts': ['Rawalpindi'],
                'budget': 5200000000,
                'kpi_target': 50000,
                'kpi_unit': 'households served',
                'duration_days': 480,
            },
            {
                'name': 'Sewerage System Upgrade - Multan',
                'description': 'Modernization of sewerage treatment and disposal system',
                'sector': 'Water & Sanitation',
                'districts': ['Multan'],
                'budget': 4700000000,
                'kpi_target': 80,
                'kpi_unit': 'treatment plants',
                'duration_days': 540,
            },
            {
                'name': 'Rural Water Supply - Sialkot',
                'description': 'Provision of clean water supply to rural communities',
                'sector': 'Water & Sanitation',
                'districts': ['Sialkot'],
                'budget': 3100000000,
                'kpi_target': 200,
                'kpi_unit': 'villages covered',
                'duration_days': 420,
            },
            
            # Health Projects
            {
                'name': 'Sehat Card THQ Expansion - Multan',
                'description': 'Expansion of Tehsil Headquarters Hospital with free maternity care under Sehat Card',
                'sector': 'Health',
                'districts': ['Multan'],
                'budget': 10000000000,
                'kpi_target': 500,
                'kpi_unit': 'beds added',
                'duration_days': 365,
            },
            {
                'name': 'Children Hospital Complex - Lahore',
                'description': 'State-of-the-art children hospital with specialized pediatric care',
                'sector': 'Health',
                'districts': ['Lahore'],
                'budget': 18000000000,
                'kpi_target': 800,
                'kpi_unit': 'beds',
                'duration_days': 900,
            },
            {
                'name': 'Rural Health Centers - Peshawar',
                'description': 'Establishment of basic health units in remote areas',
                'sector': 'Health',
                'districts': ['Peshawar'],
                'budget': 6500000000,
                'kpi_target': 50,
                'kpi_unit': 'health centers',
                'duration_days': 480,
            },
            {
                'name': 'Cancer Treatment Center - Karachi',
                'description': 'Advanced cancer treatment facility with latest equipment',
                'sector': 'Health',
                'districts': ['Karachi'],
                'budget': 12000000000,
                'kpi_target': 300,
                'kpi_unit': 'beds',
                'duration_days': 720,
            },
            {
                'name': 'Trauma Center - Quetta',
                'description': 'Emergency trauma center for accident and emergency cases',
                'sector': 'Health',
                'districts': ['Quetta'],
                'budget': 4500000000,
                'kpi_target': 100,
                'kpi_unit': 'ICU beds',
                'duration_days': 300,
            },
            
            # Education Projects
            {
                'name': 'Digital School Initiative - Rawalpindi',
                'description': 'Digitization of 500 schools with tablets and smart boards',
                'sector': 'Education',
                'districts': ['Rawalpindi'],
                'budget': 8000000000,
                'kpi_target': 500,
                'kpi_unit': 'schools digitized',
                'duration_days': 730,
            },
            {
                'name': 'University Campus - Faisalabad',
                'description': 'Construction of new university campus for technical education',
                'sector': 'Education',
                'districts': ['Faisalabad'],
                'budget': 15000000000,
                'kpi_target': 10000,
                'kpi_unit': 'student capacity',
                'duration_days': 1095,
            },
            {
                'name': 'Girls Schools Construction - Gujranwala',
                'description': 'Building new girls schools to increase female enrollment',
                'sector': 'Education',
                'districts': ['Gujranwala'],
                'budget': 7200000000,
                'kpi_target': 100,
                'kpi_unit': 'schools built',
                'duration_days': 540,
            },
            {
                'name': 'Vocational Training Centers - Sialkot',
                'description': 'Establishment of skill development centers for youth',
                'sector': 'Education',
                'districts': ['Sialkot'],
                'budget': 3500000000,
                'kpi_target': 20,
                'kpi_unit': 'training centers',
                'duration_days': 365,
            },
            {
                'name': 'Science Labs Upgrade - Islamabad',
                'description': 'Modernization of science laboratories in government schools',
                'sector': 'Education',
                'districts': ['Islamabad'],
                'budget': 2800000000,
                'kpi_target': 200,
                'kpi_unit': 'labs upgraded',
                'duration_days': 300,
            },
            
            # Electricity Projects
            {
                'name': 'Solar Power Plant - Quetta',
                'description': '100MW solar power generation facility for clean energy',
                'sector': 'Electricity',
                'districts': ['Quetta'],
                'budget': 12000000000,
                'kpi_target': 100,
                'kpi_unit': 'MW capacity',
                'duration_days': 540,
            },
            {
                'name': 'Grid Station Upgrade - Karachi',
                'description': 'Modernization of electrical grid stations for better distribution',
                'sector': 'Electricity',
                'districts': ['Karachi'],
                'budget': 9500000000,
                'kpi_target': 15,
                'kpi_unit': 'grid stations',
                'duration_days': 420,
            },
            {
                'name': 'Rural Electrification - Peshawar',
                'description': 'Extension of electricity to remote villages',
                'sector': 'Electricity',
                'districts': ['Peshawar'],
                'budget': 6800000000,
                'kpi_target': 300,
                'kpi_unit': 'villages electrified',
                'duration_days': 600,
            },
            {
                'name': 'Transmission Lines - Lahore-Faisalabad',
                'description': 'High voltage transmission lines for better connectivity',
                'sector': 'Electricity',
                'districts': ['Lahore', 'Faisalabad'],
                'budget': 8200000000,
                'kpi_target': 200,
                'kpi_unit': 'km of lines',
                'duration_days': 480,
            },
            {
                'name': 'Wind Power Project - Multan',
                'description': '50MW wind power generation facility',
                'sector': 'Electricity',
                'districts': ['Multan'],
                'budget': 7500000000,
                'kpi_target': 50,
                'kpi_unit': 'MW capacity',
                'duration_days': 450,
            },
            
            # Transport Projects
            {
                'name': 'Metro Bus System - Lahore Extension',
                'description': 'Extension of metro bus system to new routes',
                'sector': 'Transport',
                'districts': ['Lahore'],
                'budget': 25000000000,
                'kpi_target': 50,
                'kpi_unit': 'km of track',
                'duration_days': 900,
            },
            {
                'name': 'Highway Construction - Karachi-Quetta',
                'description': 'Construction of modern highway connecting major cities',
                'sector': 'Transport',
                'districts': ['Karachi', 'Quetta'],
                'budget': 35000000000,
                'kpi_target': 300,
                'kpi_unit': 'km of highway',
                'duration_days': 1200,
            },
            {
                'name': 'Airport Upgrade - Islamabad',
                'description': 'Expansion and modernization of international airport',
                'sector': 'Transport',
                'districts': ['Islamabad'],
                'budget': 22000000000,
                'kpi_target': 1,
                'kpi_unit': 'airport upgraded',
                'duration_days': 720,
            },
            {
                'name': 'Ring Road - Peshawar',
                'description': 'Construction of ring road to reduce traffic congestion',
                'sector': 'Transport',
                'districts': ['Peshawar'],
                'budget': 15000000000,
                'kpi_target': 80,
                'kpi_unit': 'km of road',
                'duration_days': 600,
            },
            {
                'name': 'Railway Track Upgrade - Rawalpindi-Faisalabad',
                'description': 'Modernization of railway infrastructure',
                'sector': 'Transport',
                'districts': ['Rawalpindi', 'Faisalabad'],
                'budget': 18000000000,
                'kpi_target': 150,
                'kpi_unit': 'km of track',
                'duration_days': 800,
            },
            
            # Security Projects
            {
                'name': 'Safe City Project - Lahore',
                'description': 'Installation of CCTV surveillance system citywide',
                'sector': 'Security',
                'districts': ['Lahore'],
                'budget': 12000000000,
                'kpi_target': 5000,
                'kpi_unit': 'cameras installed',
                'duration_days': 365,
            },
            {
                'name': 'Police Stations Modernization - Karachi',
                'description': 'Upgrading police stations with modern equipment',
                'sector': 'Security',
                'districts': ['Karachi'],
                'budget': 8500000000,
                'kpi_target': 100,
                'kpi_unit': 'stations upgraded',
                'duration_days': 480,
            },
            {
                'name': 'Border Security Enhancement - Quetta',
                'description': 'Strengthening border security infrastructure',
                'sector': 'Security',
                'districts': ['Quetta'],
                'budget': 15000000000,
                'kpi_target': 200,
                'kpi_unit': 'km border secured',
                'duration_days': 720,
            },
            {
                'name': 'Emergency Response System - Islamabad',
                'description': 'Integrated emergency response and dispatch system',
                'sector': 'Security',
                'districts': ['Islamabad'],
                'budget': 4500000000,
                'kpi_target': 1,
                'kpi_unit': 'system installed',
                'duration_days': 270,
            },
            {
                'name': 'Community Policing Centers - Gujranwala',
                'description': 'Establishment of community-based policing centers',
                'sector': 'Security',
                'districts': ['Gujranwala'],
                'budget': 3200000000,
                'kpi_target': 25,
                'kpi_unit': 'centers established',
                'duration_days': 300,
            },
        ]
        
        statuses = ['ON_TRACK', 'AT_RISK', 'DELAYED', 'COMPLETE']
        
        for i, project_data in enumerate(projects_data):
            sector = next(s for s in sectors if s.name == project_data['sector'])
            district = next(d for d in districts if d.name in project_data['districts'])
            contractor = random.choice(contractors)
            
            start_date = date.today() - timedelta(days=random.randint(30, 400))
            end_date = start_date + timedelta(days=project_data['duration_days'])
            
            # Determine status based on progress
            status = random.choice(statuses)
            if status == 'COMPLETE':
                progress = 100
                end_date_actual = end_date - timedelta(days=random.randint(0, 30))
                kpi_achieved = project_data['kpi_target']
                budget_spent = project_data['budget'] * Decimal(str(random.uniform(0.95, 1.05)))
            elif status == 'DELAYED':
                progress = random.uniform(30, 70)
                end_date_actual = None
                kpi_achieved = project_data['kpi_target'] * Decimal(str(progress / 100))
                budget_spent = project_data['budget'] * Decimal(str(progress / 100)) * Decimal(str(random.uniform(1.1, 1.3)))
            elif status == 'AT_RISK':
                progress = random.uniform(40, 75)
                end_date_actual = None
                kpi_achieved = project_data['kpi_target'] * Decimal(str(progress / 100))
                budget_spent = project_data['budget'] * Decimal(str(progress / 100)) * Decimal(str(random.uniform(0.9, 1.1)))
            else:  # ON_TRACK
                progress = random.uniform(20, 90)
                end_date_actual = None
                kpi_achieved = project_data['kpi_target'] * Decimal(str(progress / 100))
                budget_spent = project_data['budget'] * Decimal(str(progress / 100)) * Decimal(str(random.uniform(0.85, 1.0)))
            
            # Add some location variance around district center
            lat_offset = random.uniform(-0.1, 0.1)
            lng_offset = random.uniform(-0.1, 0.1)
            
            project = Project.objects.create(
                name=project_data['name'],
                description=project_data['description'],
                sector=sector,
                district=district,
                contractor=contractor,
                start_date=start_date,
                end_date_planned=end_date,
                end_date_actual=end_date_actual if status == 'COMPLETE' else None,
                status=status,
                progress_percentage=Decimal(str(round(progress, 2))),
                budget_allocated=Decimal(str(project_data['budget'])),
                budget_spent=budget_spent,
                kpi_target=Decimal(str(project_data['kpi_target'])),
                kpi_achieved=kpi_achieved,
                kpi_unit=project_data['kpi_unit'],
                latitude=Decimal(str(district.latitude + lat_offset)),
                longitude=Decimal(str(district.longitude + lng_offset)),
                created_by=admin_user,
            )
            
            self.stdout.write(f'Created project: {project.name}')

    def create_procurement_data(self):
        """Create procurement data for projects."""
        projects = Project.objects.all()
        contractors = list(Contractor.objects.all())
        
        for project in projects:
            # 70% chance of having procurement data
            if random.random() < 0.7:
                tender_amount = project.budget_allocated * Decimal(str(random.uniform(0.8, 1.0)))
                award_amount = tender_amount * Decimal(str(random.uniform(0.95, 1.15)))
                award_date = project.start_date - timedelta(days=random.randint(30, 90))
                
                procurement = Procurement.objects.create(
                    project=project,
                    tender_id=f"TND-{project.id:04d}-{random.randint(1000, 9999)}",
                    tender_title=f"Tender for {project.name}",
                    tender_amount=tender_amount,
                    award_date=award_date,
                    award_amount=award_amount,
                    contractor=project.contractor or random.choice(contractors),
                    tender_document_url=f"https://tender.gov.pk/doc-{project.id}.pdf",
                    boq_document_url=f"https://tender.gov.pk/boq-{project.id}.pdf",
                    notes=f"Procurement for {project.name} in {project.district.name}",
                )
                
                self.stdout.write(f'Created procurement: {procurement.tender_id}')

    def create_kpi_history(self):
        """Create KPI history for projects."""
        projects = Project.objects.all()
        
        for project in projects:
            # Create monthly KPI history from start date to current date
            current_date = project.start_date
            end_date = min(date.today(), project.end_date_planned)
            
            while current_date <= end_date:
                # Calculate expected progress based on time elapsed
                total_days = (project.end_date_planned - project.start_date).days
                elapsed_days = (current_date - project.start_date).days
                expected_progress = min(100, (elapsed_days / total_days) * 100)
                
                # Add some variance to make it realistic
                actual_progress = expected_progress * random.uniform(0.7, 1.2)
                kpi_achieved = project.kpi_target * Decimal(str(actual_progress / 100))
                
                KPIHistory.objects.create(
                    project=project,
                    date=current_date,
                    kpi_achieved=kpi_achieved,
                    notes=f"Monthly progress update for {current_date.strftime('%B %Y')}",
                )
                
                # Move to next month
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
            
            self.stdout.write(f'Created KPI history for: {project.name}')

    def create_feedback(self):
        """Create citizen feedback for projects."""
        projects = Project.objects.all()
        
        citizen_names = [
            "Muhammad Ali", "Fatima Sheikh", "Ahmad Khan", "Ayesha Malik",
            "Hassan Ahmed", "Zainab Ali", "Omar Farooq", "Saira Bano",
            "Bilal Hussain", "Nadia Khan", "Tariq Mahmood", "Rabia Nasir",
            "Imran Shah", "Khadija Bibi", "Zahid Iqbal", "Sobia Tariq",
            "Farhan Ahmed", "Samina Khatoon", "Waqas Ali", "Rukhsana Begum"
        ]
        
        comments_positive = [
            "Excellent work! The project is progressing well and benefiting our community.",
            "Very satisfied with the quality of work. Keep it up!",
            "Great initiative by the government. We appreciate the effort.",
            "The project has improved our quality of life significantly.",
            "Transparent process and good execution. Thank you!",
        ]
        
        comments_negative = [
            "Progress is too slow. Need more attention from authorities.",
            "Quality of work needs improvement in some areas.",
            "More community consultation would have been better.",
            "Some delays in timeline, hope it gets completed soon.",
            "Good project but execution could be better.",
        ]
        
        comments_neutral = [
            "Project is ongoing. Waiting to see the final results.",
            "So far so good. Hope it continues smoothly.",
            "Average progress. Could be faster but quality seems fine.",
            "Regular updates from officials would be appreciated.",
            "Neutral about the progress. Time will tell the results.",
        ]
        
        for project in projects:
            # Generate 2-8 feedback entries per project
            feedback_count = random.randint(2, 8)
            
            for _ in range(feedback_count):
                rating = random.randint(1, 5)
                
                if rating >= 4:
                    comment = random.choice(comments_positive)
                elif rating <= 2:
                    comment = random.choice(comments_negative)
                else:
                    comment = random.choice(comments_neutral)
                
                citizen_name = random.choice(citizen_names)
                
                Feedback.objects.create(
                    project=project,
                    citizen_name=citizen_name,
                    citizen_email=f"{citizen_name.lower().replace(' ', '.')}@citizen.pk",
                    rating=rating,
                    comment=comment,
                    is_verified=random.choice([True, False]),
                    is_public=True,
                )
            
            self.stdout.write(f'Created feedback for: {project.name}')
