from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import AdminUser, Project, Lead, Testimonial, SystemStatus, HomePageContent, FeaturedProject


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


@admin.register(HomePageContent)
class HomePageContentAdmin(admin.ModelAdmin):
    """Admin for HomePageContent model."""
    fieldsets = (
        ('Hero Section', {
            'fields': ('hero_title', 'hero_subtitle', 'hero_background_image', 'hero_cta_button_text')
        }),
        ('Statistics Section', {
            'fields': (
                ('stats_experience_value', 'stats_experience_label'),
                ('stats_projects_value', 'stats_projects_label'),
                ('stats_families_value', 'stats_families_label'),
                ('stats_sqft_value', 'stats_sqft_label'),
            )
        }),
        ('Footer Information', {
            'fields': ('footer_office_address', 'footer_phone_number', 'footer_email', 'footer_whatsapp_number')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']

    def has_add_permission(self, request):
        # Prevent creating multiple home page content records
        return not HomePageContent.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Prevent deleting home page content
        return False


@admin.register(FeaturedProject)
class FeaturedProjectAdmin(admin.ModelAdmin):
    """Admin for FeaturedProject model."""
    list_display = ['project', 'display_order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['project__title', 'project__location']
    ordering = ['display_order', '-created_at']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['project']
