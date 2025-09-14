# clients/management/commands/generate_test_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random
from clients.models import Client
from projects.models import Project
from communications.models import Communication

class Command(BaseCommand):
    help = 'Generate test data for development'
    
    def add_arguments(self, parser):
        parser.add_argument('--clients', type=int, default=20, help='Number of clients to create')
        parser.add_argument('--projects', type=int, default=30, help='Number of projects to create')
    
    def handle(self, *args, **options):
        # Sample data
        institutions = [
            'MIT', 'Stanford University', 'UC Berkeley', 'Harvard University',
            'University of Chicago', 'Yale University', 'Princeton University',
            'Columbia University', 'University of Michigan', 'Cornell University'
        ]
        
        departments = [
            'Computer Science', 'Economics', 'Political Science', 'Psychology',
            'Mathematics', 'Physics', 'Biology', 'Chemistry', 'Statistics',
            'Public Policy', 'Sociology', 'Philosophy'
        ]
        
        first_names = [
            'James', 'Maria', 'John', 'Sarah', 'Michael', 'Jennifer', 'David',
            'Lisa', 'Robert', 'Karen', 'William', 'Nancy', 'Richard', 'Betty'
        ]
        
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
            'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez'
        ]
        
        project_titles = [
            'Machine Learning in Healthcare Applications',
            'Economic Impact of Climate Change Policies',
            'Social Media Influence on Political Behavior',
            'Quantum Computing Applications in Cryptography',
            'Behavioral Economics and Consumer Decision Making',
            'Neural Networks for Natural Language Processing',
            'Public Policy Analysis Framework',
            'Statistical Methods for Big Data Analysis'
        ]
        
        # Create clients
        self.stdout.write('Creating clients...')
        for i in range(options['clients']):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            
            client = Client.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=f"{first_name.lower()}.{last_name.lower()}{i}@university.edu",
                institution=random.choice(institutions),
                department=random.choice(departments),
                title=random.choice(['PhD Candidate', 'Professor', 'Associate Professor', 'Postdoc']),
                field_of_study=random.choice(departments),
                status=random.choice(['lead', 'active', 'completed']),
                lead_source=random.choice(['website', 'referral', 'twitter', 'conference']),
                created_at=timezone.now() - timedelta(days=random.randint(1, 365))
            )
        
        # Create projects
        self.stdout.write('Creating projects...')
        clients = list(Client.objects.all())
        
        for i in range(options['projects']):
            client = random.choice(clients)
            
            project = Project.objects.create(
                client=client,
                title=random.choice(project_titles),
                project_type=random.choice(['quick_fix', 'standard_conversion', 'premium_workflow']),
                description=f"Academic project requiring LaTeX formatting and conversion services.",
                status=random.choice(['inquiry', 'quoted', 'in_progress', 'completed']),
                priority=random.choice(['low', 'normal', 'high', 'urgent']),
                quoted_amount=random.choice([200, 400, 600, 800, 1200]),
                deadline=timezone.now() + timedelta(days=random.randint(1, 30)),
                source_format=random.choice(['Word', 'LaTeX', 'Markdown']),
                target_journal=random.choice([
                    'Nature', 'Science', 'PNAS', 'American Economic Review',
                    'American Political Science Review', 'Journal of Marketing Research'
                ]),
                created_at=timezone.now() - timedelta(days=random.randint(1, 180))
            )
        
        # Update client lifetime values
        for client in Client.objects.all():
            total_value = client.projects.filter(
                status='completed'
            ).aggregate(total=models.Sum('final_amount'))['total'] or 0
            client.lifetime_value = total_value
            client.save()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {options["clients"]} clients and {options["projects"]} projects'
            )
        )
