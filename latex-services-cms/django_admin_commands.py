# clients/admin.py
from django.contrib import admin
from django.db.models import Sum, Count
from django.utils.html import format_html
from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'email', 'institution', 'status', 
        'lead_source', 'project_count', 'lifetime_value_display', 'created_at'
    ]
    list_filter = ['status', 'lead_source', 'created_at', 'institution']
    search_fields = ['first_name', 'last_name', 'email', 'institution']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Academic Information', {
            'fields': ('institution', 'department', 'title', 'field_of_study')
        }),
        ('Business Information', {
            'fields': ('status', 'lead_source', 'lifetime_value', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_contact'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            project_count=Count('projects'),
            total_value=Sum('projects__final_amount')
        )
    
    def project_count(self, obj):
        return obj.project_count
    project_count.short_description = 'Projects'
    project_count.admin_order_field = 'project_count'
    
    def lifetime_value_display(self, obj):
        value = obj.total_value or 0
        if value > 0:
            return format_html('<span style="color: green;">${:,.0f}</span>', value)
        return '$0'
    lifetime_value_display.short_description = 'LTV'
    lifetime_value_display.admin_order_field = 'total_value'

# projects/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Project, ProjectFile

class ProjectFileInline(admin.TabularInline):
    model = ProjectFile
    extra = 0
    readonly_fields = ['uploaded_at']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'client', 'project_type', 'status_display', 
        'priority_display', 'deadline_display', 'quoted_amount', 'created_at'
    ]
    list_filter = [
        'status', 'priority', 'project_type', 'created_at', 
        'client__institution'
    ]
    search_fields = ['title', 'description', 'client__first_name', 'client__last_name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ProjectFileInline]
    
    fieldsets = (
        ('Project Information', {
            'fields': ('client', 'title', 'project_type', 'description')
        }),
        ('Management', {
            'fields': ('status', 'priority', 'deadline', 'estimated_hours', 'actual_hours')
        }),
        ('Financial', {
            'fields': ('quoted_amount', 'final_amount', 'paid')
        }),
        ('Technical Details', {
            'fields': ('source_format', 'target_journal', 'special_requirements'),
            'classes': ('collapse',)
        }),
        ('Repository Links', {
            'fields': ('github_repo', 'overleaf_project'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'started_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_display(self, obj):
        colors = {
            'inquiry': 'gray',
            'quoted': 'orange',
            'approved': 'blue',
            'in_progress': 'purple',
            'review': 'teal',
            'completed': 'green',
            'cancelled': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Status'
    
    def priority_display(self, obj):
        colors = {
            'urgent': 'red',
            'high': 'orange', 
            'normal': 'green',
            'low': 'gray'
        }
        color = colors.get(obj.priority, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_priority_display()
        )
    priority_display.short_description = 'Priority'
    
    def deadline_display(self, obj):
        if not obj.deadline:
            return 'No deadline'
        
        if obj.deadline < timezone.now():
            return format_html(
                '<span style="color: red; font-weight: bold;">{} (OVERDUE)</span>',
                obj.deadline.strftime('%Y-%m-%d')
            )
        elif (obj.deadline - timezone.now()).days <= 3:
            return format_html(
                '<span style="color: orange; font-weight: bold;">{} (DUE SOON)</span>',
                obj.deadline.strftime('%Y-%m-%d')
            )
        else:
            return obj.deadline.strftime('%Y-%m-%d')
    deadline_display.short_description = 'Deadline'

@admin.register(ProjectFile)
class ProjectFileAdmin(admin.ModelAdmin):
    list_display = ['filename', 'project', 'file_type', 'version', 'uploaded_at']
    list_filter = ['file_type', 'uploaded_at']
    search_fields = ['filename', 'description', 'project__title']

# communications/admin.py
from django.contrib import admin
from .models import Communication

@admin.register(Communication)
class CommunicationAdmin(admin.ModelAdmin):
    list_display = [
        'subject', 'client', 'project', 'communication_type', 
        'direction', 'created_at'
    ]
    list_filter = [
        'communication_type', 'direction', 'created_at'
    ]
    search_fields = [
        'subject', 'content', 'client__first_name', 
        'client__last_name', 'project__title'
    ]
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Communication Details', {
            'fields': ('client', 'project', 'communication_type', 'direction', 'subject')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )

# ===== MANAGEMENT COMMANDS =====

# clients/management/__init__.py
# (empty file)

# clients/management/commands/__init__.py  
# (empty file)

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

# clients/management/commands/send_follow_up_emails.py
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from clients.models import Client
from projects.models import Project

class Command(BaseCommand):
    help = 'Send automated follow-up emails'
    
    def handle(self, *args, **options):
        # Follow up on leads after 3 days
        three_days_ago = timezone.now() - timedelta(days=3)
        stale_leads = Client.objects.filter(
            status='lead',
            created_at__lt=three_days_ago,
            last_contact__isnull=True
        )
        
        for client in stale_leads:
            subject = f"Follow-up: LaTeX Services for {client.institution}"
            message = f"""
            Hi {client.first_name},
            
            I wanted to follow up on your inquiry about LaTeX services. 
            
            I'd love to help you with your project. Would you like to schedule 
            a quick 15-minute call to discuss your needs?
            
            Best regards,
            David Adams
            latex@dadams.cc
            """
            
            # In production, you'd actually send the email:
            # send_mail(subject, message, 'latex@dadams.cc', [client.email])
            
            self.stdout.write(f"Would send follow-up to {client.email}")
        
        # Follow up on quotes after 7 days
        week_ago = timezone.now() - timedelta(days=7)
        pending_quotes = Project.objects.filter(
            status='quoted',
            updated_at__lt=week_ago
        )
        
        for project in pending_quotes:
            subject = f"Quote follow-up: {project.title}"
            message = f"""
            Hi {project.client.first_name},
            
            I wanted to check if you had any questions about the quote 
            for "{project.title}".
            
            I'm happy to adjust the scope or timeline if needed.
            
            Best regards,
            David Adams
            """
            
            self.stdout.write(f"Would send quote follow-up to {project.client.email}")
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Processed {stale_leads.count()} lead follow-ups and '
                f'{pending_quotes.count()} quote follow-ups'
            )
        )

# ===== DASHBOARD VIEWS =====

# Add to main urls.py views
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from clients.models import Client
from projects.models import Project
from communications.models import Communication

@login_required
def dashboard(request):
    # Calculate statistics
    stats = {
        'active_projects': Project.objects.filter(
            status__in=['quoted', 'approved', 'in_progress', 'review']
        ).count(),
        'monthly_revenue': Project.objects.filter(
            completed_at__gte=timezone.now().replace(day=1),
            status='completed'
        ).aggregate(total=Sum('final_amount'))['total'] or 0,
        'pending_quotes': Project.objects.filter(status='quoted').count(),
        'total_clients': Client.objects.count(),
    }
    
    # Recent projects
    recent_projects = Project.objects.select_related('client').order_by('-created_at')[:10]
    
    # Recent communications
    recent_communications = Communication.objects.select_related('client').order_by('-created_at')[:5]
    
    context = {
        'stats': stats,
        'recent_projects': recent_projects,
        'recent_communications': recent_communications,
    }
    return render(request, 'dashboard.html', context)

# .env file template
"""
# Database Configuration
DB_NAME=latex_services
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=5432

# Django Configuration  
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=latex@dadams.cc
"""

# setup.py - Installation script
"""
#!/usr/bin/env python3

import subprocess
import sys
import os

def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"✓ {command}")
    except subprocess.CalledProcessError:
        print(f"✗ Failed: {command}")
        sys.exit(1)

def main():
    print("Setting up LaTeX Services Client Management System...")
    
    # Check if Python 3.8+ is available
    if sys.version_info < (3, 8):
        print("Python 3.8+ is required")
        sys.exit(1)
    
    # Create virtual environment
    print("Creating virtual environment...")
    run_command("python -m venv latex_env")
    
    # Install requirements
    print("Installing requirements...")
    if os.name == 'nt':  # Windows
        run_command("latex_env\\Scripts\\pip install -r requirements.txt")
    else:  # Unix/Linux/Mac
        run_command("source latex_env/bin/activate && pip install -r requirements.txt")
    
    # Check PostgreSQL connection
    print("Setting up database...")
    run_command("createdb latex_services")  # Assumes PostgreSQL is installed
    
    # Django setup
    print("Running Django setup...")
    activate = "latex_env\\Scripts\\activate" if os.name == 'nt' else "source latex_env/bin/activate"
    
    commands = [
        "python manage.py makemigrations",
        "python manage.py migrate", 
        "python manage.py collectstatic --noinput",
        "python manage.py createsuperuser --noinput --username admin --email admin@example.com" 
    ]
    
    for cmd in commands:
        if os.name == 'nt':
            run_command(f"latex_env\\Scripts\\activate && {cmd}")
        else:
            run_command(f"{activate} && {cmd}")
    
    print("\n🎉 Setup complete!")
    print("Next steps:")
    print("1. Copy .env.example to .env and fill in your settings")
    print("2. Run: python manage.py generate_test_data")
    print("3. Run: python manage.py runserver")
    print("4. Visit http://localhost:8000")

if __name__ == "__main__":
    main()
"""

# ===== API ENDPOINTS FOR WEBSITE INTEGRATION =====

# api/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
import json
import logging
from clients.models import Client
from projects.models import Project
from communications.models import Communication

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def webhook_contact_form(request):
    """
    Webhook endpoint for website contact form submissions
    """
    try:
        data = json.loads(request.body)
        
        # Create or get client
        client, created = Client.objects.get_or_create(
            email=data['email'],
            defaults={
                'first_name': data.get('name', '').split(' ')[0],
                'last_name': ' '.join(data.get('name', '').split(' ')[1:]),
                'institution': data.get('institution', ''),
                'status': 'lead',
                'lead_source': 'website',
                'notes': f"Initial inquiry: {data.get('description', '')}"
            }
        )
        
        # Create project inquiry
        project = Project.objects.create(
            client=client,
            title=f"Project Inquiry - {data.get('project_type', 'Unknown')}",
            project_type=data.get('project_type', 'custom'),
            description=data.get('description', ''),
            status='inquiry',
            priority='normal' if data.get('timeline') != 'rush' else 'urgent',
        )
        
        # Log communication
        Communication.objects.create(
            client=client,
            project=project,
            communication_type='email',
            direction='inbound',
            subject=f"Website inquiry - {data.get('project_type', 'Project')}",
            content=data.get('description', '')
        )
        
        # Update client status if it was just a lead
        if client.status == 'lead':
            client.status = 'contacted'
            client.save()
        
        logger.info(f"New inquiry from {client.email}: {project.title}")
        
        return JsonResponse({
            'status': 'success',
            'project_id': project.id,
            'message': 'Inquiry received successfully'
        })
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Failed to process inquiry'
        }, status=500)

# api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('webhook/contact/', views.webhook_contact_form, name='webhook_contact'),
]

# ===== REPORTING VIEWS =====

# reports/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta, datetime
from clients.models import Client
from projects.models import Project
import json

@login_required
def revenue_report(request):
    """Monthly revenue and project completion report"""
    
    # Get last 12 months of data
    end_date = timezone.now()
    start_date = end_date - timedelta(days=365)
    
    # Monthly revenue
    monthly_data = []
    current_date = start_date.replace(day=1)
    
    while current_date <= end_date:
        next_month = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        
        revenue = Project.objects.filter(
            completed_at__gte=current_date,
            completed_at__lt=next_month,
            status='completed'
        ).aggregate(total=Sum('final_amount'))['total'] or 0
        
        project_count = Project.objects.filter(
            completed_at__gte=current_date,
            completed_at__lt=next_month,
            status='completed'
        ).count()
        
        monthly_data.append({
            'month': current_date.strftime('%Y-%m'),
            'month_name': current_date.strftime('%B %Y'),
            'revenue': float(revenue),
            'projects': project_count
        })
        
        current_date = next_month
    
    # Project type breakdown
    project_types = Project.objects.filter(
        status='completed',
        completed_at__gte=start_date
    ).values('project_type').annotate(
        count=Count('id'),
        revenue=Sum('final_amount')
    ).order_by('-revenue')
    
    # Client value analysis
    top_clients = Client.objects.annotate(
        total_value=Sum('projects__final_amount'),
        project_count=Count('projects')
    ).filter(total_value__gt=0).order_by('-total_value')[:10]
    
    context = {
        'monthly_data': monthly_data,
        'monthly_data_json': json.dumps(monthly_data),
        'project_types': project_types,
        'top_clients': top_clients,
        'total_revenue': sum(item['revenue'] for item in monthly_data),
        'total_projects': sum(item['projects'] for item in monthly_data),
        'avg_project_value': Project.objects.filter(
            status='completed', final_amount__isnull=False
        ).aggregate(avg=Avg('final_amount'))['avg'] or 0
    }
    
    return render(request, 'reports/revenue_report.html', context)

@login_required  
def pipeline_report(request):
    """Sales pipeline and conversion analysis"""
    
    # Pipeline stages
    pipeline_data = []
    for status, label in Project.STATUS_CHOICES:
        count = Project.objects.filter(status=status).count()
        total_value = Project.objects.filter(
            status=status
        ).aggregate(total=Sum('quoted_amount'))['total'] or 0
        
        pipeline_data.append({
            'status': status,
            'label': label,
            'count': count,
            'value': float(total_value)
        })
    
    # Conversion rates
    total_inquiries = Project.objects.filter(status='inquiry').count()
    total_quotes = Project.objects.filter(status__in=['quoted', 'approved', 'in_progress', 'completed']).count()
    total_completed = Project.objects.filter(status='completed').count()
    
    conversion_rates = {
        'inquiry_to_quote': (total_quotes / total_inquiries * 100) if total_inquiries else 0,
        'quote_to_completion': (total_completed / total_quotes * 100) if total_quotes else 0,
        'overall_conversion': (total_completed / total_inquiries * 100) if total_inquiries else 0
    }
    
    # Lead sources performance
    lead_sources = Client.objects.values('lead_source').annotate(
        count=Count('id'),
        converted=Count('projects', filter=Q(projects__status='completed'))
    ).order_by('-count')
    
    context = {
        'pipeline_data': pipeline_data,
        'pipeline_data_json': json.dumps(pipeline_data),
        'conversion_rates': conversion_rates,
        'lead_sources': lead_sources
    }
    
    return render(request, 'reports/pipeline_report.html', context)

# reports/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('revenue/', views.revenue_report, name='revenue_report'),
    path('pipeline/', views.pipeline_report, name='pipeline_report'),
]

# ===== EMAIL TEMPLATES =====

# templates/emails/quote_template.html
"""
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; }
        .header { background-color: #007bff; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; }
        .quote-details { background-color: #f8f9fa; padding: 15px; margin: 20px 0; }
        .total { font-size: 1.2em; font-weight: bold; color: #007bff; }
    </style>
</head>
<body>
    <div class="header">
        <h1>LaTeX Services Quote</h1>
    </div>
    <div class="content">
        <p>Dear {{ client.first_name }},</p>
        
        <p>Thank you for your interest in professional LaTeX formatting services. I'm excited to help you with "{{ project.title }}".</p>
        
        <div class="quote-details">
            <h3>Project Details:</h3>
            <ul>
                <li><strong>Project:</strong> {{ project.title }}</li>
                <li><strong>Type:</strong> {{ project.get_project_type_display }}</li>
                <li><strong>Source Format:</strong> {{ project.source_format }}</li>
                <li><strong>Target Journal:</strong> {{ project.target_journal|default:"Standard format" }}</li>
                <li><strong>Estimated Timeline:</strong> {{ project.estimated_hours }} hours</li>
            </ul>
            
            <div class="total">
                Total Investment: ${{ project.quoted_amount }}
            </div>
        </div>
        
        <h3>What's Included:</h3>
        <ul>
            <li>Complete document conversion to LaTeX</li>
            <li>Proper formatting for your target publication</li>
            <li>Bibliography integration and citation formatting</li>
            <li>Figure and table optimization</li>
            <li>Overleaf project setup for easy collaboration</li>
            <li>One round of revisions included</li>
        </ul>
        
        <p>This quote is valid for 14 days. To proceed, simply reply to this email or call me at your convenience.</p>
        
        <p>I look forward to helping make your research look as professional as it deserves!</p>
        
        <p>Best regards,<br>
        David Adams<br>
        latex@dadams.cc<br>
        dadams.cc</p>
    </div>
</body>
</html>
"""

# ===== DEPLOYMENT SCRIPTS =====

# deploy.sh
"""
#!/bin/bash
# Simple deployment script for VPS/cloud deployment

set -e

echo "🚀 Deploying LaTeX Services CMS..."

# Pull latest code
git pull origin main

# Activate virtual environment
source latex_env/bin/activate

# Install/upgrade requirements
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart services (adjust for your setup)
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo "✅ Deployment complete!"
"""

# docker-compose.yml
"""
version: '3.8'

services:
  db:
    image: postgres:13
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      POSTGRES_DB: latex_services
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/code
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - DEBUG=1
      - DB_HOST=db

volumes:
  postgres_data:
"""

# Dockerfile
"""
FROM python:3.11-slim

WORKDIR /code

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
"""