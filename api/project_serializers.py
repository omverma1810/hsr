from rest_framework import serializers
from django.db import transaction
from django.db.models import Max
from .models import (
    Project, ProjectGalleryImage, ProjectFloorPlan,
    PROJECT_CONFIGURATIONS, PROJECT_AMENITIES
)


class ProjectGalleryImageSerializer(serializers.ModelSerializer):
    """Serializer for project gallery images."""

    image = serializers.SerializerMethodField()

    class Meta:
        model = ProjectGalleryImage
        fields = ['id', 'image_url', 'image_file', 'image', 'caption', 'display_order', 'created_at']
        read_only_fields = ['id', 'created_at', 'image']

    def get_image(self, obj):
        """Return the actual image URL (absolute URL)."""
        image_url = obj.image
        
        # Return as-is if already absolute (Cloudinary URLs)
        if image_url and (image_url.startswith('http://') or image_url.startswith('https://')):
            return image_url
        
        # Only build absolute URI for relative URLs (local media files)
        if image_url and not image_url.startswith('http'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(image_url)
            # Fallback: construct URL from settings
            from django.conf import settings
            base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
            return f"{base_url}{image_url}"
        
        return image_url


class ProjectFloorPlanSerializer(serializers.ModelSerializer):
    """Serializer for project floor plans."""

    file_path = serializers.SerializerMethodField()

    class Meta:
        model = ProjectFloorPlan
        fields = ['id', 'title', 'file_url', 'file', 'file_path', 'display_order', 'created_at']
        read_only_fields = ['id', 'created_at', 'file_path']

    def get_file_path(self, obj):
        """Return the actual file URL (absolute URL)."""
        file_url = obj.file_path
        
        # Return as-is if already absolute (Cloudinary URLs)
        if file_url and (file_url.startswith('http://') or file_url.startswith('https://')):
            return file_url
        
        # Only build absolute URI for relative URLs (local media files)
        if file_url and not file_url.startswith('http'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(file_url)
            # Fallback: construct URL from settings
            from django.conf import settings
            base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
            return f"{base_url}{file_url}"
        
        return file_url


class ProjectListSerializer(serializers.ModelSerializer):
    """Serializer for project list view (lightweight)."""

    hero_image = serializers.SerializerMethodField()
    hero_image_url = serializers.SerializerMethodField()
    configurations = serializers.SerializerMethodField()
    amenities = serializers.SerializerMethodField()
    configurations_list = serializers.SerializerMethodField()
    amenities_list = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'title', 'slug', 'location', 'rera_number', 'status',
            'hero_image', 'hero_image_url', 'is_featured', 
            'configurations', 'configurations_list', 
            'amenities', 'amenities_list',
            'view_count', 'created_by_name', 'created_at', 'updated_at'
        ]

    def get_hero_image(self, obj):
        """Return hero image URL (absolute URL)."""
        hero_image_url = obj.hero_image
        
        # Return as-is if already absolute (Cloudinary URLs)
        if hero_image_url and (hero_image_url.startswith('http://') or hero_image_url.startswith('https://')):
            return hero_image_url
        
        # Only build absolute URI for relative URLs (local media files)
        if hero_image_url and not hero_image_url.startswith('http'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(hero_image_url)
            # Fallback: construct URL from settings
            from django.conf import settings
            base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
            return f"{base_url}{hero_image_url}"
        
        return hero_image_url

    def get_hero_image_url(self, obj):
        """Return hero_image_url for frontend compatibility (absolute URL)."""
        hero_url = obj.hero_image_url or (obj.hero_image_file.url if obj.hero_image_file else None)
        
        # Return as-is if already absolute (Cloudinary URLs)
        if hero_url and (hero_url.startswith('http://') or hero_url.startswith('https://')):
            return hero_url
        
        # Only build absolute URI for relative URLs (local media files)
        if hero_url and not hero_url.startswith('http'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(hero_url)
            # Fallback: construct URL from settings
            from django.conf import settings
            base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
            return f"{base_url}{hero_url}"
        
        return hero_url

    def get_configurations(self, obj):
        """Return configurations as array for frontend."""
        return obj.get_configurations_list()

    def get_amenities(self, obj):
        """Return amenities as array for frontend."""
        return obj.get_amenities_list()

    def get_configurations_list(self, obj):
        return obj.get_configurations_list()

    def get_amenities_list(self, obj):
        return obj.get_amenities_list()


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed project view."""

    hero_image = serializers.SerializerMethodField()
    hero_image_url = serializers.SerializerMethodField()
    brochure = serializers.SerializerMethodField()
    gallery_images = ProjectGalleryImageSerializer(many=True, read_only=True)
    floor_plans = ProjectFloorPlanSerializer(many=True, read_only=True)
    configurations = serializers.SerializerMethodField()
    amenities = serializers.SerializerMethodField()
    configurations_list = serializers.SerializerMethodField()
    amenities_list = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    updated_by_name = serializers.CharField(source='updated_by.full_name', read_only=True)

    # Related counts
    leads_count = serializers.SerializerMethodField()
    testimonials_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'title', 'slug', 'location', 'rera_number', 'description', 'status',
            'hero_image_url', 'hero_image_file', 'hero_image',
            'brochure_url', 'brochure_file', 'brochure',
            'configurations', 'configurations_list',
            'amenities', 'amenities_list',
            'is_featured', 'view_count',
            'gallery_images', 'floor_plans',
            'created_by', 'created_by_name', 'updated_by', 'updated_by_name',
            'leads_count', 'testimonials_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'view_count', 'created_at', 'updated_at']

    def get_hero_image(self, obj):
        """Return hero image URL (absolute URL)."""
        hero_image_url = obj.hero_image
        
        # Return as-is if already absolute (Cloudinary URLs)
        if hero_image_url and (hero_image_url.startswith('http://') or hero_image_url.startswith('https://')):
            return hero_image_url
        
        # Only build absolute URI for relative URLs (local media files)
        if hero_image_url and not hero_image_url.startswith('http'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(hero_image_url)
            # Fallback: construct URL from settings
            from django.conf import settings
            base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
            return f"{base_url}{hero_image_url}"
        
        return hero_image_url

    def get_hero_image_url(self, obj):
        """Return hero_image_url for frontend compatibility (absolute URL)."""
        hero_url = obj.hero_image_url or (obj.hero_image_file.url if obj.hero_image_file else None)
        
        # Return as-is if already absolute (Cloudinary URLs)
        if hero_url and (hero_url.startswith('http://') or hero_url.startswith('https://')):
            return hero_url
        
        # Only build absolute URI for relative URLs (local media files)  
        if hero_url and not hero_url.startswith('http'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(hero_url)
            # Fallback: construct URL from settings
            from django.conf import settings
            base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
            return f"{base_url}{hero_url}"
        
        return hero_url

    def get_brochure(self, obj):
        """Return brochure URL (absolute URL)."""
        brochure_url = obj.brochure
        
        # Return as-is if already absolute (Cloudinary URLs)
        if brochure_url and (brochure_url.startswith('http://') or brochure_url.startswith('https://')):
            return brochure_url
        
        # Only build absolute URI for relative URLs (local media files)
        if brochure_url and not brochure_url.startswith('http'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(brochure_url)
            # Fallback: construct URL from settings
            from django.conf import settings
            base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
            return f"{base_url}{brochure_url}"
        
        return brochure_url

    def get_configurations(self, obj):
        """Return configurations as array for frontend."""
        return obj.get_configurations_list()

    def get_amenities(self, obj):
        """Return amenities as array for frontend."""
        return obj.get_amenities_list()

    def get_configurations_list(self, obj):
        return obj.get_configurations_list()

    def get_amenities_list(self, obj):
        return obj.get_amenities_list()

    def get_leads_count(self, obj):
        return obj.leads.filter(is_deleted=False).count()

    def get_testimonials_count(self, obj):
        return obj.testimonials.filter(is_deleted=False).count()


class ProjectCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating projects."""

    # Optional: Accept configurations and amenities as lists
    configurations_list = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )
    amenities_list = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Project
        fields = [
            'title', 'location', 'rera_number', 'description', 'status',
            'hero_image_url', 'hero_image_file',
            'brochure_url', 'brochure_file',
            'configurations', 'configurations_list',
            'amenities', 'amenities_list',
            'is_featured'
        ]

    def validate_rera_number(self, value):
        """Validate RERA number uniqueness."""
        instance = self.instance
        if instance:
            # Update scenario
            if Project.objects.filter(rera_number=value, is_deleted=False).exclude(pk=instance.pk).exists():
                raise serializers.ValidationError("A project with this RERA number already exists.")
        else:
            # Create scenario
            if Project.objects.filter(rera_number=value, is_deleted=False).exists():
                raise serializers.ValidationError("A project with this RERA number already exists.")
        return value

    def validate_configurations_list(self, value):
        """Validate configurations list."""
        valid_configs = [config[0] for config in PROJECT_CONFIGURATIONS]
        for config in value:
            if config not in valid_configs:
                raise serializers.ValidationError(f"Invalid configuration: {config}")
        return value

    def validate_amenities_list(self, value):
        """Validate amenities list."""
        valid_amenities = [amenity[0] for amenity in PROJECT_AMENITIES]
        for amenity in value:
            if amenity not in valid_amenities:
                raise serializers.ValidationError(f"Invalid amenity: {amenity}")
        return value

    def validate(self, data):
        """Additional validation."""
        # Must provide either URL or file for hero image
        if not data.get('hero_image_url') and not data.get('hero_image_file'):
            if not self.instance:  # Only required on create
                raise serializers.ValidationError({
                    'hero_image': 'Either hero_image_url or hero_image_file must be provided.'
                })

        return data

    def create(self, validated_data):
        """Create project with configurations and amenities."""
        configurations_list = validated_data.pop('configurations_list', [])
        amenities_list = validated_data.pop('amenities_list', [])
        is_featured = validated_data.pop('is_featured', False)

        # Convert lists to dict format if provided
        if configurations_list:
            validated_data['configurations'] = {config: True for config in configurations_list}

        if amenities_list:
            validated_data['amenities'] = {amenity: True for amenity in amenities_list}

        # Set created_by from request user
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
            validated_data['updated_by'] = request.user

        # Create project
        project = super().create(validated_data)

        # Create FeaturedProject entry if is_featured is True
        if is_featured:
            from .models import FeaturedProject
            # Get the highest display_order and add 1
            max_order = FeaturedProject.objects.aggregate(
                max_order=Max('display_order')
            )['max_order'] or 0
            FeaturedProject.objects.create(
                project=project,
                display_order=max_order + 1,
                is_active=True
            )

        return project

    def update(self, instance, validated_data):
        """Update project with configurations and amenities."""
        configurations_list = validated_data.pop('configurations_list', None)
        amenities_list = validated_data.pop('amenities_list', None)
        is_featured = validated_data.pop('is_featured', None)

        # Update configurations if provided as list
        if configurations_list is not None:
            validated_data['configurations'] = {config: True for config in configurations_list}

        # Update amenities if provided as list
        if amenities_list is not None:
            validated_data['amenities'] = {amenity: True for amenity in amenities_list}

        # Set updated_by from request user
        request = self.context.get('request')
        if request and request.user:
            validated_data['updated_by'] = request.user

        # Update project
        project = super().update(instance, validated_data)

        # Handle FeaturedProject entry based on is_featured status
        from .models import FeaturedProject
        
        if is_featured is True:
            # Create FeaturedProject entry if it doesn't exist
            try:
                featured_entry = project.featured_placement
                # Ensure existing entry is active
                featured_entry.is_active = True
                featured_entry.save()
            except FeaturedProject.DoesNotExist:
                # Get the highest display_order and add 1
                max_order = FeaturedProject.objects.aggregate(
                    max_order=Max('display_order')
                )['max_order'] or 0
                FeaturedProject.objects.create(
                    project=project,
                    display_order=max_order + 1,
                    is_active=True
                )
        elif is_featured is False:
            # Remove FeaturedProject entry if is_featured is set to False
            try:
                project.featured_placement.delete()
            except FeaturedProject.DoesNotExist:
                pass  # Already not featured, nothing to do

        return project


class AddGalleryImageSerializer(serializers.Serializer):
    """Serializer for adding gallery images."""
    image_url = serializers.URLField(required=False, allow_null=True)
    image_file = serializers.ImageField(required=False, allow_null=True)
    caption = serializers.CharField(max_length=255, required=False, allow_blank=True)
    display_order = serializers.IntegerField(default=0)

    def validate(self, data):
        """Must provide either URL or file."""
        if not data.get('image_url') and not data.get('image_file'):
            raise serializers.ValidationError({
                'image': 'Either image_url or image_file must be provided.'
            })
        return data


class AddFloorPlanSerializer(serializers.Serializer):
    """Serializer for adding floor plans."""
    title = serializers.CharField(max_length=255)
    file_url = serializers.URLField(required=False, allow_null=True)
    file = serializers.FileField(required=False, allow_null=True)
    display_order = serializers.IntegerField(default=0)

    def validate(self, data):
        """Must provide either URL or file."""
        if not data.get('file_url') and not data.get('file'):
            raise serializers.ValidationError({
                'file': 'Either file_url or file must be provided.'
            })
        return data


class ProjectConfigurationsSerializer(serializers.Serializer):
    """Serializer for available configurations."""
    key = serializers.CharField()
    label = serializers.CharField()


class ProjectAmenitiesSerializer(serializers.Serializer):
    """Serializer for available amenities."""
    key = serializers.CharField()
    label = serializers.CharField()


class BulkActionSerializer(serializers.Serializer):
    """Serializer for bulk actions."""
    project_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    action = serializers.ChoiceField(choices=['delete', 'restore', 'feature', 'unfeature', 'change_status'])
    status = serializers.ChoiceField(
        choices=['upcoming', 'ongoing', 'completed'],
        required=False
    )

    def validate(self, data):
        """Validate action-specific requirements."""
        if data['action'] == 'change_status' and not data.get('status'):
            raise serializers.ValidationError({
                'status': 'Status is required when action is change_status.'
            })
        return data
