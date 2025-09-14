# clients/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.client_list, name='client_list'),
    path('<int:pk>/', views.client_detail, name='client_detail'),
    path('add/', views.client_create, name='client_create'),
    path('<int:pk>/edit/', views.client_edit, name='client_edit'),
]

# projects/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.project_list, name='project_list'),
    path('<int:pk>/', views.project_detail, name='project_detail'),
    path('add/', views.project_create, name='project_create'),
    path('<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('<int:pk>/files/upload/', views.upload_file, name='upload_file'),
]

# communications/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.communication_list, name='communication_list'),
    path('add/', views.communication_create, name='communication_create'),
    path('<int:pk>/', views.communication_detail, name='communication_detail'),
]

# ===== TEMPLATES =====

# templates/base.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}LaTeX Services CMS{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        .sidebar {
            min-height: 100vh;
            background-color: #f8f9fa;
            border-right: 1px solid #dee2e6;
        }
        .main-content {
            min-height: 100vh;
        }
        .status-badge {
            font-size: 0.75rem;
            padding: 0.25rem 0.5rem;
        }
        .priority-urgent { border-left: 4px solid #dc3545; }
        .priority-high { border-left: 4px solid #fd7e14; }
        .priority-normal { border-left: 4px solid #20c997; }
        .priority-low { border-left: 4px solid #6c757d; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <div class="col-md-2 sidebar p-3">
                <h5 class="mb-4">LaTeX Services</h5>
                <ul class="nav nav-pills flex-column">
                    <li class="nav-item mb-2">
                        <a class="nav-link {% if request.resolver_match.url_name == 'dashboard' %}active{% endif %}" 
                           href="{% url 'dashboard' %}">
                            <i class="fas fa-tachometer-alt me-2"></i>Dashboard
                        </a>
                    </li>
                    <li class="nav-item mb-2">
                        <a class="nav-link {% if 'client' in request.resolver_match.url_name %}active{% endif %}" 
                           href="{% url 'client_list' %}">
                            <i class="fas fa-users me-2"></i>Clients
                        </a>
                    </li>
                    <li class="nav-item mb-2">
                        <a class="nav-link {% if 'project' in request.resolver_match.url_name %}active{% endif %}" 
                           href="{% url 'project_list' %}">
                            <i class="fas fa-project-diagram me-2"></i>Projects
                        </a>
                    </li>
                    <li class="nav-item mb-2">
                        <a class="nav-link {% if 'communication' in request.resolver_match.url_name %}active{% endif %}" 
                           href="{% url 'communication_list' %}">
                            <i class="fas fa-comments me-2"></i>Communications
                        </a>
                    </li>
                    <li class="nav-item mb-2">
                        <a class="nav-link" href="/admin/">
                            <i class="fas fa-cog me-2"></i>Admin
                        </a>
                    </li>
                </ul>
            </div>
            
            <!-- Main Content -->
            <div class="col-md-10 main-content p-4">
                <!-- Messages -->
                {% if messages %}
                    {% for message in messages %}
                        <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                            {{ message }}
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        </div>
                    {% endfor %}
                {% endif %}
                
                {% block content %}{% endblock %}
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>

# templates/dashboard.html
{% extends 'base.html' %}
{% load humanize %}

{% block title %}Dashboard - LaTeX Services{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <h1>Dashboard</h1>
    <div>
        <a href="{% url 'client_create' %}" class="btn btn-primary me-2">
            <i class="fas fa-user-plus"></i> Add Client
        </a>
        <a href="{% url 'project_create' %}" class="btn btn-success">
            <i class="fas fa-plus"></i> New Project
        </a>
    </div>
</div>

<!-- Statistics Cards -->
<div class="row mb-4">
    <div class="col-md-3">
        <div class="card bg-primary text-white">
            <div class="card-body">
                <div class="d-flex justify-content-between">
                    <div>
                        <h3>{{ stats.active_projects }}</h3>
                        <p class="mb-0">Active Projects</p>
                    </div>
                    <div class="align-self-center">
                        <i class="fas fa-users fa-2x"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Recent Activity -->
<div class="row">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Recent Projects</h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>Project</th>
                                <th>Client</th>
                                <th>Status</th>
                                <th>Deadline</th>
                                <th>Value</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for project in recent_projects %}
                            <tr class="priority-{{ project.priority }}">
                                <td>
                                    <a href="{% url 'project_detail' project.pk %}">{{ project.title }}</a>
                                </td>
                                <td>{{ project.client.full_name }}</td>
                                <td>
                                    <span class="badge bg-secondary status-badge">{{ project.get_status_display }}</span>
                                </td>
                                <td>
                                    {% if project.deadline %}
                                        {{ project.deadline|date:"M d, Y" }}
                                        {% if project.is_overdue %}
                                            <span class="badge bg-danger ms-1">Overdue</span>
                                        {% endif %}
                                    {% else %}
                                        No deadline
                                    {% endif %}
                                </td>
                                <td>${{ project.quoted_amount|default:"—" }}</td>
                            </tr>
                            {% empty %}
                            <tr>
                                <td colspan="5" class="text-center text-muted">No recent projects</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-md-4">
        <div class="card mb-4">
            <div class="card-header">
                <h5 class="mb-0">Quick Actions</h5>
            </div>
            <div class="card-body">
                <div class="d-grid gap-2">
                    <a href="{% url 'client_create' %}" class="btn btn-outline-primary">
                        <i class="fas fa-user-plus"></i> Add New Client
                    </a>
                    <a href="{% url 'project_create' %}" class="btn btn-outline-success">
                        <i class="fas fa-plus"></i> Create Project
                    </a>
                    <a href="{% url 'communication_create' %}" class="btn btn-outline-info">
                        <i class="fas fa-envelope"></i> Log Communication
                    </a>
                    <a href="{% url 'project_list' %}?overdue=1" class="btn btn-outline-warning">
                        <i class="fas fa-exclamation-triangle"></i> View Overdue
                    </a>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Recent Communications</h5>
            </div>
            <div class="card-body">
                {% for comm in recent_communications %}
                <div class="d-flex mb-3">
                    <div class="flex-shrink-0">
                        <i class="fas fa-{{ comm.communication_type }} text-muted"></i>
                    </div>
                    <div class="flex-grow-1 ms-3">
                        <div class="fw-bold">{{ comm.subject }}</div>
                        <small class="text-muted">
                            {{ comm.client.full_name }} - {{ comm.created_at|timesince }} ago
                        </small>
                    </div>
                </div>
                {% empty %}
                <p class="text-muted">No recent communications</p>
                {% endfor %}
            </div>
        </div>
    </div>
</div>
{% endblock %}

# templates/clients/client_list.html
{% extends 'base.html' %}
{% load humanize %}

{% block title %}Clients - LaTeX Services{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <h1>Clients</h1>
    <a href="{% url 'client_create' %}" class="btn btn-primary">
        <i class="fas fa-plus"></i> Add Client
    </a>
</div>

<!-- Filters -->
<div class="card mb-4">
    <div class="card-body">
        <form method="get" class="row g-3">
            <div class="col-md-6">
                <input type="text" class="form-control" name="search" 
                       placeholder="Search clients..." value="{{ search }}">
            </div>
            <div class="col-md-4">
                <select name="status" class="form-select">
                    <option value="">All Statuses</option>
                    {% for value, label in status_choices %}
                        <option value="{{ value }}" {% if value == status %}selected{% endif %}>
                            {{ label }}
                        </option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-md-2">
                <button type="submit" class="btn btn-outline-secondary w-100">
                    <i class="fas fa-search"></i> Filter
                </button>
            </div>
        </form>
    </div>
</div>

<!-- Clients Table -->
<div class="card">
    <div class="card-body">
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Institution</th>
                        <th>Status</th>
                        <th>Projects</th>
                        <th>Total Value</th>
                        <th>Last Contact</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for client in clients %}
                    <tr>
                        <td>
                            <div class="fw-bold">{{ client.full_name }}</div>
                            <small class="text-muted">{{ client.email }}</small>
                        </td>
                        <td>{{ client.institution|default:"—" }}</td>
                        <td>
                            <span class="badge bg-{% if client.status == 'active' %}success{% elif client.status == 'lead' %}warning{% else %}secondary{% endif %}">
                                {{ client.get_status_display }}
                            </span>
                        </td>
                        <td>{{ client.project_count }}</td>
                        <td>${{ client.total_value|default:0|floatformat:0|intcomma }}</td>
                        <td>
                            {% if client.last_contact %}
                                {{ client.last_contact|timesince }} ago
                            {% else %}
                                Never
                            {% endif %}
                        </td>
                        <td>
                            <a href="{% url 'client_detail' client.pk %}" class="btn btn-sm btn-outline-primary">
                                <i class="fas fa-eye"></i>
                            </a>
                            <a href="{% url 'client_edit' client.pk %}" class="btn btn-sm btn-outline-secondary">
                                <i class="fas fa-edit"></i>
                            </a>
                        </td>
                    </tr>
                    {% empty %}
                    <tr>
                        <td colspan="7" class="text-center text-muted py-4">
                            No clients found. <a href="{% url 'client_create' %}">Add your first client</a>!
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}

# templates/projects/project_list.html
{% extends 'base.html' %}
{% load humanize %}

{% block title %}Projects - LaTeX Services{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <h1>Projects</h1>
    <a href="{% url 'project_create' %}" class="btn btn-primary">
        <i class="fas fa-plus"></i> New Project
    </a>
</div>

<!-- Filters -->
<div class="card mb-4">
    <div class="card-body">
        <form method="get" class="row g-3">
            <div class="col-md-3">
                <select name="status" class="form-select">
                    <option value="">All Statuses</option>
                    {% for value, label in status_choices %}
                        <option value="{{ value }}" {% if value == status %}selected{% endif %}>
                            {{ label }}
                        </option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-md-3">
                <select name="priority" class="form-select">
                    <option value="">All Priorities</option>
                    {% for value, label in priority_choices %}
                        <option value="{{ value }}" {% if value == priority %}selected{% endif %}>
                            {{ label }}
                        </option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-md-3">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" name="overdue" value="1" 
                           {% if show_overdue %}checked{% endif %}>
                    <label class="form-check-label">
                        Show only overdue
                    </label>
                </div>
            </div>
            <div class="col-md-3">
                <button type="submit" class="btn btn-outline-secondary w-100">
                    <i class="fas fa-filter"></i> Filter
                </button>
            </div>
        </form>
    </div>
</div>

<!-- Projects Table -->
<div class="card">
    <div class="card-body">
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>Project</th>
                        <th>Client</th>
                        <th>Type</th>
                        <th>Status</th>
                        <th>Priority</th>
                        <th>Deadline</th>
                        <th>Value</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for project in projects %}
                    <tr class="priority-{{ project.priority }}">
                        <td>
                            <div class="fw-bold">{{ project.title }}</div>
                            <small class="text-muted">Created {{ project.created_at|date:"M d, Y" }}</small>
                        </td>
                        <td>
                            <a href="{% url 'client_detail' project.client.pk %}">
                                {{ project.client.full_name }}
                            </a>
                        </td>
                        <td>
                            <span class="badge bg-light text-dark">{{ project.get_project_type_display }}</span>
                        </td>
                        <td>
                            <span class="badge bg-{% if project.status == 'completed' %}success{% elif project.status == 'in_progress' %}primary{% elif project.status == 'cancelled' %}danger{% else %}secondary{% endif %}">
                                {{ project.get_status_display }}
                            </span>
                        </td>
                        <td>
                            <span class="badge bg-{% if project.priority == 'urgent' %}danger{% elif project.priority == 'high' %}warning{% elif project.priority == 'normal' %}success{% else %}secondary{% endif %}">
                                {{ project.get_priority_display }}
                            </span>
                        </td>
                        <td>
                            {% if project.deadline %}
                                {{ project.deadline|date:"M d, Y" }}
                                {% if project.is_overdue %}
                                    <br><span class="badge bg-danger">Overdue</span>
                                {% elif project.days_until_deadline <= 3 %}
                                    <br><span class="badge bg-warning">Due Soon</span>
                                {% endif %}
                            {% else %}
                                No deadline
                            {% endif %}
                        </td>
                        <td>${{ project.quoted_amount|default:"—" }}</td>
                        <td>
                            <a href="{% url 'project_detail' project.pk %}" class="btn btn-sm btn-outline-primary">
                                <i class="fas fa-eye"></i>
                            </a>
                            <a href="{% url 'project_edit' project.pk %}" class="btn btn-sm btn-outline-secondary">
                                <i class="fas fa-edit"></i>
                            </a>
                        </td>
                    </tr>
                    {% empty %}
                    <tr>
                        <td colspan="8" class="text-center text-muted py-4">
                            No projects found. <a href="{% url 'project_create' %}">Create your first project</a>!
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}
                        <i class="fas fa-project-diagram fa-2x"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card bg-success text-white">
            <div class="card-body">
                <div class="d-flex justify-content-between">
                    <div>
                        <h3>${{ stats.monthly_revenue|floatformat:0|intcomma }}</h3>
                        <p class="mb-0">This Month</p>
                    </div>
                    <div class="align-self-center">
                        <i class="fas fa-dollar-sign fa-2x"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card bg-warning text-white">
            <div class="card-body">
                <div class="d-flex justify-content-between">
                    <div>
                        <h3>{{ stats.pending_quotes }}</h3>
                        <p class="mb-0">Pending Quotes</p>
                    </div>
                    <div class="align-self-center">
                        <i class="fas fa-clock fa-2x"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card bg-info text-white">
            <div class="card-body">
                <div class="d-flex justify-content-between">
                    <div>
                        <h3>{{ stats.total_clients }}</h3>
                        <p class="mb-0">Total Clients</p>
                    </div>
                    <div class="align-self-center">