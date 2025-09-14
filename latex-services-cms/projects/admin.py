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
