from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import AdminUser, Project, Lead, Testimonial, SystemStatus


@admin.register(AdminUser)
class AdminUserAdmin(BaseUserAdmin):
    """Custom admin for AdminUser model."""

    list_display = ['email', 'full_name', 'role', 'is_active', 'is_superuser', 'date_joined']
    list_filter = ['is_active', 'is_superuser', 'role', 'date_joined']
    search_fields = ['email', 'full_name']
    ordering = ['-date_joined']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'role', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )

    readonly_fields = ['date_joined', 'last_login']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin for Project model."""
    list_display = ['title', 'location', 'rera_number', 'status', 'is_featured', 'created_at']
    list_filter = ['status', 'is_featured', 'created_at']
    search_fields = ['title', 'location', 'rera_number']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    """Admin for Lead model."""
    list_display = ['name', 'email', 'phone', 'project', 'status', 'source', 'created_at']
    list_filter = ['status', 'source', 'created_at']
    search_fields = ['name', 'email', 'phone']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['project', 'contacted_by']


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    """Admin for Testimonial model."""
    list_display = ['customer_name', 'project', 'is_active', 'display_order', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['customer_name', 'quote']
    ordering = ['display_order', '-created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SystemStatus)
class SystemStatusAdmin(admin.ModelAdmin):
    """Admin for SystemStatus model."""
    list_display = ['website_status', 'whatsapp_integration_active', 'contact_forms_working', 'last_backup_at']
    readonly_fields = ['created_at', 'updated_at']

    def has_add_permission(self, request):
        # Prevent creating multiple system status records
        return not SystemStatus.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Prevent deleting system status
        return False
