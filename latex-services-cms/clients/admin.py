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
