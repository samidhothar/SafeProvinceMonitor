"""
Management command to update KPI data for demo purposes.
This simulates real-time updates by randomly updating project KPIs.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
import random

from dashboard.models import Project, KPIHistory


class Command(BaseCommand):
    help = 'Update KPI data for demo purposes (simulates real-time updates)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Number of projects to update (default: 5)',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Update all active projects',
        )

    def handle(self, *args, **options):
        """Execute the command."""
        if options['all']:
            projects = Project.objects.exclude(status='COMPLETE')
        else:
            projects = Project.objects.exclude(status='COMPLETE').order_by('?')[:options['count']]
        
        if not projects.exists():
            self.stdout.write(
                self.style.WARNING('No active projects found to update.')
            )
            return
        
        updated_count = 0
        
        for project in projects:
            # Skip if project hasn't started yet
            if project.start_date > date.today():
                continue
            
            # Calculate expected progress based on timeline
            total_days = (project.end_date_planned - project.start_date).days
            elapsed_days = (date.today() - project.start_date).days
            expected_progress = min(100, (elapsed_days / total_days) * 100)
            
            # Add realistic variance to progress (±5%)
            current_progress = float(project.progress_percentage)
            max_increase = min(5.0, expected_progress - current_progress + 2.0)
            
            if max_increase > 0:
                progress_increase = random.uniform(0, max_increase)
                new_progress = min(100, current_progress + progress_increase)
                
                # Update project progress
                project.progress_percentage = Decimal(str(round(new_progress, 2)))
                
                # Update KPI achievement proportionally
                kpi_ratio = new_progress / 100
                new_kpi = project.kpi_target * Decimal(str(kpi_ratio))
                project.kpi_achieved = new_kpi
                
                # Update budget spent (slightly random within reasonable bounds)
                budget_ratio = new_progress / 100
                variance = random.uniform(0.9, 1.1)  # ±10% variance
                new_budget_spent = project.budget_allocated * Decimal(str(budget_ratio * variance))
                project.budget_spent = min(new_budget_spent, project.budget_allocated * Decimal('1.2'))
                
                # Update status based on progress and timeline
                project.status = self.calculate_status(project, new_progress, expected_progress)
                
                # Mark as complete if 100% progress
                if new_progress >= 100:
                    project.status = 'COMPLETE'
                    project.end_date_actual = date.today()
                
                project.save()
                
                # Create KPI history entry
                KPIHistory.objects.create(
                    project=project,
                    date=date.today(),
                    kpi_achieved=project.kpi_achieved,
                    notes=f"Automated update - Progress: {new_progress:.1f}%",
                )
                
                updated_count += 1
                
                self.stdout.write(
                    f'Updated {project.name}: {new_progress:.1f}% '
                    f'(KPI: {float(new_kpi):.1f}/{float(project.kpi_target)})'
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated {updated_count} projects.'
            )
        )

    def calculate_status(self, project, actual_progress, expected_progress):
        """Calculate project status based on progress and timeline."""
        progress_gap = expected_progress - actual_progress
        
        # If significantly behind schedule (>15% gap)
        if progress_gap > 15:
            return 'DELAYED'
        
        # If moderately behind schedule (5-15% gap)
        elif progress_gap > 5:
            return 'AT_RISK'
        
        # If project should be at risk based on KPI criteria
        elif project.should_be_at_risk:
            return 'AT_RISK'
        
        # Otherwise, on track
        else:
            return 'ON_TRACK'
