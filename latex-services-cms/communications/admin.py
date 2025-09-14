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
