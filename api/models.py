from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from django.utils.text import slugify
import os
import uuid


class AdminUserManager(BaseUserManager):
    """Custom manager for AdminUser model."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user."""
        if not email:
            raise ValueError('Email address is required')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'Super Admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')

        return self.create_user(email, password, **extra_fields)


class AdminUser(AbstractBaseUser, PermissionsMixin):
    """Custom Admin User model with email as the primary identifier."""

    email = models.EmailField(unique=True, db_index=True)
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=50, default='Admin')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = AdminUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        db_table = 'admin_users'
        verbose_name = 'Admin User'
        verbose_name_plural = 'Admin Users'

    def __str__(self):
        return f"{self.full_name} ({self.email})"


# Abstract Base Models for Reusability
class TimeStampedModel(models.Model):
    """Abstract base model with created and updated timestamps."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteManager(models.Manager):
    """Manager that excludes soft-deleted records."""
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class SoftDeleteModel(models.Model):
    """Abstract base model with soft delete functionality."""
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()  # Access all records including deleted

    class Meta:
        abstract = True

    def soft_delete(self):
        """Soft delete the record."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None
        self.save()


# Helper functions for file uploads
def project_hero_image_path(instance, filename):
    """Generate path for project hero images."""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('projects', str(instance.id), 'hero', filename)


def project_gallery_image_path(instance, filename):
    """Generate path for project gallery images."""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('projects', str(instance.project.id), 'gallery', filename)


def project_floor_plan_path(instance, filename):
    """Generate path for floor plan files."""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('projects', str(instance.project.id), 'floor_plans', filename)


def project_brochure_path(instance, filename):
    """Generate path for project brochure."""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('projects', str(instance.id), 'brochure', filename)


class Project(TimeStampedModel, SoftDeleteModel):
    """Enhanced Project model with complete fields for real estate projects."""

    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    ]

    # Basic Information
    title = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    location = models.CharField(max_length=255, db_index=True)
    rera_number = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text='Unique RERA registration number'
    )
    description = models.TextField(help_text='Detailed project description')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='upcoming',
        db_index=True
    )

    # Media Fields
    hero_image_url = models.URLField(
        blank=True,
        null=True,
        help_text='External URL for hero image (if not uploading file)'
    )
    hero_image_file = models.ImageField(
        upload_to=project_hero_image_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
        help_text='Upload hero image file'
    )

    brochure_url = models.URLField(
        blank=True,
        null=True,
        help_text='External URL for brochure PDF (if not uploading file)'
    )
    brochure_file = models.FileField(
        upload_to=project_brochure_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['pdf'])],
        help_text='Upload brochure PDF file'
    )

    # Configurations (JSON field for flexibility)
    configurations = models.JSONField(
        default=dict,
        help_text='Project configurations: {1BHK: true, 2BHK: false, ...}'
    )

    # Amenities (JSON field for flexibility)
    amenities = models.JSONField(
        default=dict,
        help_text='Project amenities: {swimming_pool: true, gym: false, ...}'
    )

    # Settings
    is_featured = models.BooleanField(
        default=False,
        db_index=True,
        help_text='Featured projects appear on homepage'
    )

    # Tracking
    created_by = models.ForeignKey(
        'AdminUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_projects',
        help_text='Admin user who created this project'
    )
    updated_by = models.ForeignKey(
        'AdminUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_projects',
        help_text='Admin user who last updated this project'
    )

    # Metadata
    view_count = models.IntegerField(default=0, help_text='Number of times project was viewed')

    class Meta:
        db_table = 'projects'
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'is_deleted']),
            models.Index(fields=['is_featured', 'is_deleted']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.location}"

    def save(self, *args, **kwargs):
        """Auto-generate slug from title if not provided."""
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure unique slug
            original_slug = self.slug
            counter = 1
            while Project.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    @property
    def hero_image(self):
        """Return hero image URL (file upload takes precedence over URL)."""
        if self.hero_image_file:
            return self.hero_image_file.url
        return self.hero_image_url

    @property
    def brochure(self):
        """Return brochure URL (file upload takes precedence over URL)."""
        if self.brochure_file:
            return self.brochure_file.url
        return self.brochure_url

    def get_configurations_list(self):
        """Return list of selected configurations."""
        if not self.configurations:
            return []
        return [key for key, value in self.configurations.items() if value]

    def get_amenities_list(self):
        """Return list of selected amenities."""
        if not self.amenities:
            return []
        return [key for key, value in self.amenities.items() if value]

    def increment_view_count(self):
        """Increment view count."""
        self.view_count += 1
        self.save(update_fields=['view_count'])


class Lead(TimeStampedModel, SoftDeleteModel):
    """Model for customer leads/inquiries."""

    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('closed', 'Closed'),
    ]

    SOURCE_CHOICES = [
        ('contact_form', 'Contact Form'),
        ('whatsapp', 'WhatsApp'),
        ('phone_call', 'Phone Call'),
        ('walk_in', 'Walk In'),
    ]

    # Contact Information
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Invalid phone number format")]
    )

    # Inquiry Details
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='leads')
    message = models.TextField()
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='contact_form')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')

    # Tracking
    contacted_at = models.DateTimeField(null=True, blank=True)
    contacted_by = models.ForeignKey(AdminUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='contacted_leads')
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'leads'
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['email']),
            models.Index(fields=['phone']),
        ]

    def __str__(self):
        return f"{self.name} - {self.project.title if self.project else 'No Project'}"


class Testimonial(TimeStampedModel, SoftDeleteModel):
    """Model for customer testimonials."""

    customer_name = models.CharField(max_length=255)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='testimonials')
    quote = models.TextField()
    customer_photo = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)

    class Meta:
        db_table = 'testimonials'
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return f"{self.customer_name} - {self.project.title}"


class SystemStatus(TimeStampedModel):
    """Model to track system status and configurations."""

    # System Health
    website_status = models.BooleanField(default=True)
    whatsapp_integration_active = models.BooleanField(default=True)
    contact_forms_working = models.BooleanField(default=True)

    # Backup Information
    last_backup_at = models.DateTimeField(auto_now_add=True)

    # Session Configuration
    session_timeout = models.IntegerField(default=60, help_text="Session timeout in minutes")

    # Maintenance Mode
    maintenance_mode = models.BooleanField(default=False)

    class Meta:
        db_table = 'system_status'
        verbose_name = 'System Status'
        verbose_name_plural = 'System Status'

    def __str__(self):
        return f"System Status - {self.updated_at}"

    @classmethod
    def get_current(cls):
        """Get or create current system status."""
        status, created = cls.objects.get_or_create(id=1)
        return status


class HomePageContent(TimeStampedModel):
    """
    Model for home page content management.
    Single instance model - only one record should exist.
    """

    # Hero Section
    hero_title = models.CharField(
        max_length=255,
        default='Premium Living Spaces in Karimnagar',
        help_text='Main hero section title'
    )
    hero_subtitle = models.TextField(
        default='Discover your dream home with HSR Green Homes - where quality meets comfort',
        help_text='Hero section subtitle/description'
    )
    hero_background_image = models.URLField(
        blank=True,
        null=True,
        help_text='URL for hero section background image'
    )
    hero_cta_button_text = models.CharField(
        max_length=50,
        default='Explore Projects',
        help_text='Call-to-action button text'
    )

    # Statistics Section
    stats_experience_value = models.CharField(
        max_length=20,
        default='15+',
        help_text='Years of experience (e.g., 15+)'
    )
    stats_experience_label = models.CharField(
        max_length=100,
        default='Years of Excellence',
        help_text='Label for experience stat'
    )

    stats_projects_value = models.CharField(
        max_length=20,
        default='50+',
        help_text='Number of projects completed (e.g., 50+)'
    )
    stats_projects_label = models.CharField(
        max_length=100,
        default='Projects Completed',
        help_text='Label for projects stat'
    )

    stats_families_value = models.CharField(
        max_length=20,
        default='2000+',
        help_text='Number of happy families (e.g., 2000+)'
    )
    stats_families_label = models.CharField(
        max_length=100,
        default='Happy Families',
        help_text='Label for families stat'
    )

    stats_sqft_value = models.CharField(
        max_length=20,
        default='10L+',
        help_text='Square feet delivered (e.g., 10L+)'
    )
    stats_sqft_label = models.CharField(
        max_length=100,
        default='Sq.Ft Delivered',
        help_text='Label for sqft stat'
    )

    # Footer Information
    footer_office_address = models.TextField(
        default='HSR Green Homes, Karimnagar, Telangana 505001',
        help_text='Complete office address for footer'
    )
    footer_phone_number = models.CharField(
        max_length=20,
        default='+91 9876543210',
        help_text='Primary contact phone number'
    )
    footer_email = models.EmailField(
        default='info@hsrgreenhomes.com',
        help_text='Primary contact email'
    )
    footer_whatsapp_number = models.CharField(
        max_length=20,
        default='+91 9876543210',
        help_text='WhatsApp contact number'
    )

    class Meta:
        db_table = 'home_page_content'
        verbose_name = 'Home Page Content'
        verbose_name_plural = 'Home Page Content'

    def __str__(self):
        return f"Home Page Content - Last Updated: {self.updated_at}"

    def save(self, *args, **kwargs):
        """Ensure only one instance exists."""
        if not self.pk and HomePageContent.objects.exists():
            raise ValidationError('Only one HomePageContent instance is allowed.')
        return super().save(*args, **kwargs)

    @classmethod
    def get_current(cls):
        """Get or create the single home page content instance."""
        content, created = cls.objects.get_or_create(id=1)
        return content


class FeaturedProject(TimeStampedModel):
    """
    Model to manage which projects are featured on the homepage.
    Links to existing Project model with display order.
    """

    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name='featured_placement',
        help_text='Project to feature on homepage'
    )
    display_order = models.IntegerField(
        default=0,
        help_text='Order in which to display (lower number = higher priority)'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this featured project is currently active'
    )

    class Meta:
        db_table = 'featured_projects'
        verbose_name = 'Featured Project'
        verbose_name_plural = 'Featured Projects'
        ordering = ['display_order', '-created_at']
        unique_together = ['project']  # Each project can only be featured once

    def __str__(self):
        return f"Featured: {self.project.title} (Order: {self.display_order})"


class ProjectGalleryImage(TimeStampedModel, SoftDeleteModel):
    """Model for project gallery images."""

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='gallery_images'
    )

    image_url = models.URLField(
        blank=True,
        null=True,
        help_text='External URL for gallery image'
    )
    image_file = models.ImageField(
        upload_to=project_gallery_image_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
        help_text='Upload gallery image file'
    )

    caption = models.CharField(max_length=255, blank=True)
    display_order = models.IntegerField(default=0)

    class Meta:
        db_table = 'project_gallery_images'
        verbose_name = 'Gallery Image'
        verbose_name_plural = 'Gallery Images'
        ordering = ['display_order', 'created_at']

    def __str__(self):
        return f"{self.project.title} - Gallery Image {self.id}"

    @property
    def image(self):
        """Return image URL (file upload takes precedence)."""
        if self.image_file:
            return self.image_file.url
        return self.image_url


class ProjectFloorPlan(TimeStampedModel, SoftDeleteModel):
    """Model for project floor plans."""

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='floor_plans'
    )

    title = models.CharField(max_length=255, help_text='e.g., 2BHK Floor Plan')

    file_url = models.URLField(
        blank=True,
        null=True,
        help_text='External URL for floor plan file'
    )
    file = models.FileField(
        upload_to=project_floor_plan_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])],
        help_text='Upload floor plan file (PDF or Image)'
    )

    display_order = models.IntegerField(default=0)

    class Meta:
        db_table = 'project_floor_plans'
        verbose_name = 'Floor Plan'
        verbose_name_plural = 'Floor Plans'
        ordering = ['display_order', 'created_at']

    def __str__(self):
        return f"{self.project.title} - {self.title}"

    @property
    def file_path(self):
        """Return file URL (file upload takes precedence)."""
        if self.file:
            return self.file.url
        return self.file_url


# Configuration and Amenity Choices (for validation and frontend)
PROJECT_CONFIGURATIONS = [
    ('1bhk', '1BHK'),
    ('2bhk', '2BHK'),
    ('3bhk', '3BHK'),
    ('4bhk', '4BHK'),
    ('villa', 'Villa'),
    ('duplex', 'Duplex'),
]

PROJECT_AMENITIES = [
    ('swimming_pool', 'Swimming Pool'),
    ('childrens_play_area', "Children's Play Area"),
    ('security', 'Security'),
    ('parking', 'Parking'),
    ('jogging_track', 'Jogging Track'),
    ('gym', 'Gym'),
    ('clubhouse', 'Clubhouse'),
    ('power_backup', 'Power Backup'),
    ('garden', 'Garden'),
    ('community_hall', 'Community Hall'),
]
