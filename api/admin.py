from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    AdminUser, Project, Lead, Testimonial, SystemStatus,
    HomePageContent, FeaturedProject, ContactSettings,
    ProjectGalleryImage, ProjectFloorPlan, PageHeroImages
)


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


class ProjectGalleryImageInline(admin.TabularInline):
    """Inline admin for project gallery images."""
    model = ProjectGalleryImage
    extra = 1
    fields = ['image_url', 'image_file', 'caption', 'display_order', 'is_deleted']
    readonly_fields = []


class ProjectFloorPlanInline(admin.TabularInline):
    """Inline admin for project floor plans."""
    model = ProjectFloorPlan
    extra = 1
    fields = ['title', 'file_url', 'file', 'display_order', 'is_deleted']
    readonly_fields = []


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Enhanced admin for Project model."""

    list_display = [
        'title', 'location', 'rera_number', 'status',
        'is_featured', 'view_count', 'created_by', 'created_at'
    ]
    list_filter = ['status', 'is_featured', 'is_deleted', 'created_at']
    search_fields = ['title', 'location', 'rera_number', 'description']
    ordering = ['-created_at']
    readonly_fields = ['slug', 'view_count', 'created_at', 'updated_at', 'created_by', 'updated_by']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'location', 'rera_number', 'description', 'status')
        }),
        ('Media', {
            'fields': (
                ('hero_image_url', 'hero_image_file'),
                ('brochure_url', 'brochure_file'),
            )
        }),
        ('Configurations & Amenities', {
            'fields': ('configurations', 'amenities')
        }),
        ('Settings', {
            'fields': ('is_featured', 'view_count')
        }),
        ('Tracking', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Soft Delete', {
            'fields': ('is_deleted', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [ProjectGalleryImageInline, ProjectFloorPlanInline]

    def save_model(self, request, obj, form, change):
        """Auto-set created_by and updated_by."""
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


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


@admin.register(PageHeroImages)
class PageHeroImagesAdmin(admin.ModelAdmin):
    """Admin for PageHeroImages model."""
    fieldsets = (
        ('Page Hero Images', {
            'fields': ('projects_hero_image_url', 'about_hero_image_url', 'about_our_story_image_url', 'contact_hero_image_url')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']

    def has_add_permission(self, request):
        # Prevent creating multiple page hero images records
        return not PageHeroImages.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Prevent deleting page hero images
        return False


@admin.register(ProjectGalleryImage)
class ProjectGalleryImageAdmin(admin.ModelAdmin):
    """Admin for ProjectGalleryImage model."""

    list_display = ['id', 'project', 'caption', 'display_order', 'created_at']
    list_filter = ['is_deleted', 'created_at']
    search_fields = ['project__title', 'caption']
    ordering = ['project', 'display_order', 'created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ProjectFloorPlan)
class ProjectFloorPlanAdmin(admin.ModelAdmin):
    """Admin for ProjectFloorPlan model."""

    list_display = ['id', 'project', 'title', 'display_order', 'created_at']
    list_filter = ['is_deleted', 'created_at']
    search_fields = ['project__title', 'title']
    ordering = ['project', 'display_order', 'created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(FeaturedProject)
class FeaturedProjectAdmin(admin.ModelAdmin):
    """Admin for FeaturedProject model."""
    list_display = ['project', 'display_order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['project__title', 'project__location']
    ordering = ['display_order', '-created_at']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['project']


@admin.register(ContactSettings)
class ContactSettingsAdmin(admin.ModelAdmin):
    """Admin for ContactSettings model."""
    fieldsets = (
        ('WhatsApp Settings', {
            'fields': ('whatsapp_enabled', 'whatsapp_number', 'whatsapp_business_hours', 'whatsapp_auto_reply')
        }),
        ('Phone Settings', {
            'fields': ('primary_phone', 'secondary_phone', 'toll_free_number', 'phone_business_hours')
        }),
        ('Email Settings', {
            'fields': (
                'info_email', 'sales_email', 'support_email',
                'email_auto_reply_enabled', 'email_auto_reply_subject', 'email_auto_reply_message'
            )
        }),
        ('Address Settings', {
            'fields': (
                'street_address', 'area', 'city', 'state', 'pincode', 'country', 'google_maps_embed_code'
            )
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'instagram_url', 'twitter_url', 'linkedin_url', 'youtube_url')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']

    def has_add_permission(self, request):
        # Prevent creating multiple contact settings records
        return not ContactSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Prevent deleting contact settings
        return False
