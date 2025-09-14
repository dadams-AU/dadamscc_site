# requirements.txt
Django==4.2.7
psycopg2-binary==2.9.9
django-environ==0.11.2
Pillow==10.1.0
django-crispy-forms==2.1
crispy-bootstrap5==0.7
django-extensions==3.2.3
python-decouple==3.8

# ===== SETTINGS =====
# latex_services/settings.py

import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=lambda v: [s.strip() for s in v.split(',')])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    
    # Third party
    'crispy_forms',
    'crispy_bootstrap5',
    'django_extensions',
    
    # Local apps
    'clients',
    'projects',
    'communications',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'latex_services.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='latex_services'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='password'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Los_Angeles'  # Adjust for your timezone
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='latex@dadams.cc')

# ===== MODELS =====

# clients/models.py
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

class Client(models.Model):
    LEAD_SOURCE_CHOICES = [
        ('website', 'Website Form'),
        ('referral', 'Referral'),
        ('twitter', 'Twitter/X'),
        ('bluesky', 'Bluesky'),
        ('conference', 'Conference'),
        ('email', 'Direct Email'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('lead', 'Lead'),
        ('contacted', 'Contacted'),
        ('active', 'Active Client'),
        ('completed', 'Completed Projects'),
        ('inactive', 'Inactive'),
    ]
    
    # Basic Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # Academic Information
    institution = models.CharField(max_length=200, blank=True)
    department = models.CharField(max_length=200, blank=True)
    title = models.CharField(max_length=100, blank=True, help_text="e.g., PhD Candidate, Professor, etc.")
    field_of_study = models.CharField(max_length=200, blank=True)
    
    # Business Information
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='lead')
    lead_source = models.CharField(max_length=20, choices=LEAD_SOURCE_CHOICES, default='website')
    lifetime_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_contact = models.DateTimeField(null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True, help_text="Internal notes about this client")
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.institution})"
    
    def get_absolute_url(self):
        return reverse('client_detail', kwargs={'pk': self.pk})
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def active_projects(self):
        return self.projects.filter(status__in=['quoted', 'in_progress', 'review'])

# projects/models.py
from django.db import models
from django.urls import reverse
from django.utils import timezone
from clients.models import Client

class Project(models.Model):
    PROJECT_TYPE_CHOICES = [
        ('quick_fix', 'Quick Fix ($200)'),
        ('standard_conversion', 'Standard Conversion ($400-600)'),
        ('premium_workflow', 'Premium Workflow ($800-1200)'),
        ('custom', 'Custom Project'),
    ]
    
    STATUS_CHOICES = [
        ('inquiry', 'Initial Inquiry'),
        ('quoted', 'Quote Sent'),
        ('approved', 'Quote Approved'),
        ('in_progress', 'In Progress'),
        ('review', 'Client Review'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # Basic Information
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    project_type = models.CharField(max_length=30, choices=PROJECT_TYPE_CHOICES)
    description = models.TextField()
    
    # Project Management
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inquiry')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    
    # Financial
    quoted_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    paid = models.BooleanField(default=False)
    
    # Timeline
    deadline = models.DateTimeField(null=True, blank=True)
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    actual_hours = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    
    # Technical Details
    source_format = models.CharField(max_length=50, blank=True, help_text="e.g., Word, LaTeX, Markdown")
    target_journal = models.CharField(max_length=200, blank=True)
    special_requirements = models.TextField(blank=True)
    
    # Repository Information
    github_repo = models.URLField(blank=True)
    overleaf_project = models.URLField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.client.full_name}"
    
    def get_absolute_url(self):
        return reverse('project_detail', kwargs={'pk': self.pk})
    
    @property
    def is_overdue(self):
        return self.deadline and self.deadline < timezone.now() and self.status != 'completed'
    
    @property
    def days_until_deadline(self):
        if not self.deadline:
            return None
        delta = self.deadline - timezone.now()
        return delta.days

class ProjectFile(models.Model):
    FILE_TYPE_CHOICES = [
        ('source', 'Source Document'),
        ('output', 'LaTeX Output'),
        ('reference', 'Reference Material'),
        ('revision', 'Revision'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files')
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES)
    file = models.FileField(upload_to='project_files/%Y/%m/')
    filename = models.CharField(max_length=255)
    description = models.CharField(max_length=500, blank=True)
    version = models.CharField(max_length=20, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.filename} - {self.project.title}"

# communications/models.py
from django.db import models
from django.contrib.auth.models import User
from clients.models import Client
from projects.models import Project

class Communication(models.Model):
    COMMUNICATION_TYPE_CHOICES = [
        ('email', 'Email'),
        ('call', 'Phone Call'),
        ('meeting', 'Meeting'),
        ('note', 'Internal Note'),
    ]
    
    DIRECTION_CHOICES = [
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
        ('internal', 'Internal'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='communications')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='communications', null=True, blank=True)
    
    communication_type = models.CharField(max_length=20, choices=COMMUNICATION_TYPE_CHOICES)
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.communication_type} - {self.subject} ({self.created_at.strftime('%Y-%m-%d')})"

# ===== VIEWS =====

# latex_services/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    path('clients/', include('clients.urls')),
    path('projects/', include('projects.urls')),
    path('communications/', include('communications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# clients/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.utils import timezone
from .models import Client
from .forms import ClientForm
from projects.models import Project

@login_required
def client_list(requests):
    clients = Client.objects.select_related().prefetch_related('projects')
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        clients = clients.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(institution__icontains=search)
        )
    
    # Status filter
    status = request.GET.get('status')
    if status:
        clients = clients.filter(status=status)
    
    # Add aggregated data
    clients = clients.annotate(
        project_count=Count('projects'),
        total_value=Sum('projects__final_amount')
    )
    
    context = {
        'clients': clients,
        'search': search,
        'status': status,
        'status_choices': Client.STATUS_CHOICES,
    }
    return render(request, 'clients/client_list.html', context)

@login_required
def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    projects = client.projects.all()
    recent_communications = client.communications.all()[:5]
    
    context = {
        'client': client,
        'projects': projects,
        'recent_communications': recent_communications,
    }
    return render(request, 'clients/client_detail.html', context)

@login_required
def client_create(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save()
            messages.success(request, f'Client {client.full_name} created successfully!')
            return redirect('client_detail', pk=client.pk)
    else:
        form = ClientForm()
    
    return render(request, 'clients/client_form.html', {'form': form, 'title': 'Add New Client'})

# projects/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import Project
from .forms import ProjectForm

@login_required
def project_list(request):
    projects = Project.objects.select_related('client').all()
    
    # Status filter
    status = request.GET.get('status')
    if status:
        projects = projects.filter(status=status)
    
    # Priority filter
    priority = request.GET.get('priority')
    if priority:
        projects = projects.filter(priority=priority)
    
    # Overdue projects
    show_overdue = request.GET.get('overdue')
    if show_overdue:
        projects = projects.filter(
            deadline__lt=timezone.now(),
            status__in=['quoted', 'approved', 'in_progress', 'review']
        )
    
    context = {
        'projects': projects,
        'status': status,
        'priority': priority,
        'show_overdue': show_overdue,
        'status_choices': Project.STATUS_CHOICES,
        'priority_choices': Project.PRIORITY_CHOICES,
    }
    return render(request, 'projects/project_list.html', context)

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    files = project.files.all()
    communications = project.communications.all()
    
    context = {
        'project': project,
        'files': files,
        'communications': communications,
    }
    return render(request, 'projects/project_detail.html', context)

# ===== FORMS =====

# clients/forms.py
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from .models import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'institution', 'department', 'title', 'field_of_study',
            'status', 'lead_source', 'notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('email', css_class='form-group col-md-8 mb-0'),
                Column('phone', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('institution', css_class='form-group col-md-6 mb-0'),
                Column('department', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('title', css_class='form-group col-md-6 mb-0'),
                Column('field_of_study', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('status', css_class='form-group col-md-6 mb-0'),
                Column('lead_source', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'notes',
            Submit('submit', 'Save Client', css_class='btn-primary')
        )

# projects/forms.py
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from .models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'client', 'title', 'project_type', 'description',
            'status', 'priority', 'deadline', 'quoted_amount',
            'source_format', 'target_journal', 'special_requirements'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'special_requirements': forms.Textarea(attrs={'rows': 3}),
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'client',
            'title',
            Row(
                Column('project_type', css_class='form-group col-md-6 mb-0'),
                Column('status', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'description',
            Row(
                Column('priority', css_class='form-group col-md-4 mb-0'),
                Column('deadline', css_class='form-group col-md-4 mb-0'),
                Column('quoted_amount', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('source_format', css_class='form-group col-md-6 mb-0'),
                Column('target_journal', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'special_requirements',
            Submit('submit', 'Save Project', css_class='btn-primary')
        )
