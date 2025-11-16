from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    AdminUser, Project, Lead, Testimonial, SystemStatus,
    HomePageContent, FeaturedProject,
    ProjectGalleryImage, ProjectFloorPlan
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
    """Enhanced admin for Lead model with Phase 5 fields."""
    list_display = [
        'name', 'email', 'phone', 'project', 'status',
        'priority', 'source', 'next_follow_up', 'follow_up_count', 'created_at'
    ]
    list_filter = ['status', 'priority', 'source', 'preferred_contact_method', 'created_at']
    search_fields = ['name', 'email', 'phone', 'notes']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'contacted_at', 'follow_up_count']
    autocomplete_fields = ['project', 'contacted_by']

    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone', 'preferred_contact_method')
        }),
        ('Lead Details', {
            'fields': ('project', 'message', 'source', 'status', 'priority')
        }),
        ('Follow-up Management', {
            'fields': ('next_follow_up', 'follow_up_count', 'notes')
        }),
        ('Tracking', {
            'fields': ('contacted_at', 'contacted_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Soft Delete', {
            'fields': ('is_deleted', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_contacted', 'mark_as_qualified', 'mark_as_closed']

    def mark_as_contacted(self, request, queryset):
        """Mark selected leads as contacted."""
        updated = 0
        for lead in queryset:
            if lead.status != 'contacted':
                lead.mark_contacted(admin_user=request.user)
                updated += 1
        self.message_user(request, f'{updated} leads marked as contacted.')
    mark_as_contacted.short_description = 'Mark as Contacted'

    def mark_as_qualified(self, request, queryset):
        """Mark selected leads as qualified."""
        updated = queryset.update(status='qualified')
        self.message_user(request, f'{updated} leads marked as qualified.')
    mark_as_qualified.short_description = 'Mark as Qualified'

    def mark_as_closed(self, request, queryset):
        """Mark selected leads as closed."""
        updated = queryset.update(status='closed')
        self.message_user(request, f'{updated} leads marked as closed.')
    mark_as_closed.short_description = 'Mark as Closed'


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    """Enhanced admin for Testimonial model with Phase 5 fields."""
    list_display = [
        'customer_name', 'project', 'rating', 'verified',
        'is_active', 'display_order', 'created_at'
    ]
    list_filter = ['is_active', 'verified', 'rating', 'created_at']
    search_fields = ['customer_name', 'quote']
    ordering = ['display_order', '-created_at']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Customer Information', {
            'fields': ('customer_name', 'customer_photo', 'project')
        }),
        ('Testimonial Content', {
            'fields': ('quote', 'rating', 'verified')
        }),
        ('Display Settings', {
            'fields': ('is_active', 'display_order')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Soft Delete', {
            'fields': ('is_deleted', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_verified', 'mark_as_unverified', 'activate_testimonials', 'deactivate_testimonials']

    def mark_as_verified(self, request, queryset):
        """Mark selected testimonials as verified."""
        updated = queryset.update(verified=True)
        self.message_user(request, f'{updated} testimonials marked as verified.')
    mark_as_verified.short_description = 'Mark as Verified'

    def mark_as_unverified(self, request, queryset):
        """Mark selected testimonials as unverified."""
        updated = queryset.update(verified=False)
        self.message_user(request, f'{updated} testimonials marked as unverified.')
    mark_as_unverified.short_description = 'Mark as Unverified'

    def activate_testimonials(self, request, queryset):
        """Activate selected testimonials."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} testimonials activated.')
    activate_testimonials.short_description = 'Activate Testimonials'

    def deactivate_testimonials(self, request, queryset):
        """Deactivate selected testimonials."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} testimonials deactivated.')
    deactivate_testimonials.short_description = 'Deactivate Testimonials'


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
