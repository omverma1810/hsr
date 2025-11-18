from rest_framework import serializers
from .models import HomePageContent, FeaturedProject, Project, Testimonial, PageHeroImages


class HeroSectionSerializer(serializers.ModelSerializer):
    """Serializer for hero section only."""

    class Meta:
        model = HomePageContent
        fields = [
            'hero_title',
            'hero_subtitle',
            'hero_background_image',
            'hero_cta_button_text'
        ]


class StatisticsSectionSerializer(serializers.ModelSerializer):
    """Serializer for statistics section - returns flat fields as frontend expects."""

    class Meta:
        model = HomePageContent
        fields = [
            'stats_experience_value',
            'stats_experience_label',
            'stats_projects_value',
            'stats_projects_label',
            'stats_families_value',
            'stats_families_label',
            'stats_sqft_value',
            'stats_sqft_label'
        ]


class FooterInfoSerializer(serializers.ModelSerializer):
    """Serializer for footer information only."""
    
    footer_email_address = serializers.EmailField(source='footer_email', required=False)

    class Meta:
        model = HomePageContent
        fields = [
            'footer_office_address',
            'footer_phone_number',
            'footer_email',
            'footer_email_address',
            'footer_whatsapp_number'
        ]
        extra_kwargs = {
            'footer_email': {'write_only': True, 'required': False}
        }
    
    def to_representation(self, instance):
        """Add footer_email_address to response."""
        ret = super().to_representation(instance)
        ret['footer_email_address'] = instance.footer_email
        return ret


class HomePageContentSerializer(serializers.ModelSerializer):
    """Complete home page content with nested sections."""

    hero_section = serializers.SerializerMethodField()
    statistics_section = serializers.SerializerMethodField()
    footer_info = serializers.SerializerMethodField()

    class Meta:
        model = HomePageContent
        fields = [
            'id',
            'hero_section',
            'statistics_section',
            'footer_info',
            'created_at',
            'updated_at'
        ]

    def get_hero_section(self, obj):
        return HeroSectionSerializer(obj).data

    def get_statistics_section(self, obj):
        return StatisticsSectionSerializer(obj).data

    def get_footer_info(self, obj):
        return FooterInfoSerializer(obj).data


class HomePageContentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating home page content."""

    class Meta:
        model = HomePageContent
        fields = [
            'hero_title',
            'hero_subtitle',
            'hero_background_image',
            'hero_cta_button_text',
            'stats_experience_value',
            'stats_experience_label',
            'stats_projects_value',
            'stats_projects_label',
            'stats_families_value',
            'stats_families_label',
            'stats_sqft_value',
            'stats_sqft_label',
            'footer_office_address',
            'footer_phone_number',
            'footer_email',
            'footer_whatsapp_number'
        ]


class ProjectBasicSerializer(serializers.ModelSerializer):
    """Basic project info for featured projects."""
    
    hero_image_url = serializers.SerializerMethodField()
    slug = serializers.CharField(read_only=True)

    class Meta:
        model = Project
        fields = [
            'id',
            'title',
            'slug',
            'location',
            'rera_number',
            'description',
            'status',
            'hero_image',
            'hero_image_url',
            'created_at'
        ]
    
    def get_hero_image_url(self, obj):
        """Return hero_image_url for frontend compatibility."""
        return obj.hero_image_url or (obj.hero_image_file.url if obj.hero_image_file else None)


class CompletedProjectSerializer(serializers.ModelSerializer):
    """Serializer for completed projects on homepage."""
    
    hero_image_url = serializers.SerializerMethodField()
    slug = serializers.CharField(read_only=True)
    configurations = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id',
            'title',
            'slug',
            'location',
            'rera_number',
            'status',
            'hero_image_url',
            'configurations',
            'price',
            'created_at'
        ]
    
    def get_hero_image_url(self, obj):
        """Return hero_image_url for frontend compatibility."""
        return obj.hero_image_url or (obj.hero_image_file.url if obj.hero_image_file else None)
    
    def get_configurations(self, obj):
        """Return configurations as array for frontend."""
        return obj.get_configurations_list()
    
    def get_price(self, obj):
        """Return price if available, otherwise None."""
        # Price field doesn't exist in Project model, return None
        return None


class FeaturedProjectSerializer(serializers.ModelSerializer):
    """Serializer for featured projects with full project details."""

    project = ProjectBasicSerializer(read_only=True)
    project_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = FeaturedProject
        fields = [
            'id',
            'project',
            'project_id',
            'display_order',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_project_id(self, value):
        """Validate that the project exists and is not deleted."""
        try:
            project = Project.objects.get(id=value, is_deleted=False)
        except Project.DoesNotExist:
            raise serializers.ValidationError("Project does not exist or has been deleted.")
        return value


class AddFeaturedProjectSerializer(serializers.ModelSerializer):
    """Serializer for adding a new featured project."""

    class Meta:
        model = FeaturedProject
        fields = ['project', 'display_order', 'is_active']

    def validate_project(self, value):
        """Validate that the project is not already featured."""
        if FeaturedProject.objects.filter(project=value).exists():
            raise serializers.ValidationError("This project is already featured.")

        if value.is_deleted:
            raise serializers.ValidationError("Cannot feature a deleted project.")

        return value


class TestimonialDisplaySerializer(serializers.ModelSerializer):
    """Serializer for displaying testimonials on homepage - matches frontend interface."""

    name = serializers.CharField(source='customer_name', read_only=True)
    testimonial_text = serializers.CharField(source='quote', read_only=True)
    avatar_url = serializers.CharField(source='customer_photo', read_only=True, allow_null=True)
    project = serializers.SerializerMethodField()
    rating = serializers.IntegerField(default=5, read_only=True)  # Default rating for compatibility

    class Meta:
        model = Testimonial
        fields = [
            'id',
            'name',
            'testimonial_text',
            'rating',
            'avatar_url',
            'project',
            'display_order'
        ]
    
    def get_project(self, obj):
        """Return project as nested object for frontend compatibility."""
        if obj.project:
            return {
                'id': obj.project.id,
                'title': obj.project.title
            }
        return None


class CompleteHomePageSerializer(serializers.Serializer):
    """
    Complete homepage data in a single optimized API call.
    Combines hero section, statistics, featured projects, completed projects, and testimonials.
    Note: Footer data is managed separately via contact settings API.
    """

    hero_section = serializers.SerializerMethodField()
    statistics = serializers.SerializerMethodField()
    featured_projects = serializers.SerializerMethodField()
    completed_projects = serializers.SerializerMethodField()
    testimonials = serializers.SerializerMethodField()

    def get_hero_section(self, obj):
        return HeroSectionSerializer(obj).data

    def get_statistics(self, obj):
        return StatisticsSectionSerializer(obj).data

    def get_featured_projects(self, obj):
        featured = FeaturedProject.objects.filter(
            is_active=True,
            project__is_deleted=False,
            project__status__in=['ongoing', 'completed']  # Exclude upcoming projects
        ).select_related('project').order_by('display_order')[:6]
        return FeaturedProjectSerializer(featured, many=True).data

    def get_completed_projects(self, obj):
        """Get completed projects for homepage display."""
        from .models import Project
        completed = Project.objects.filter(
            status='completed',
            is_deleted=False
        ).order_by('-created_at')[:6]
        return CompletedProjectSerializer(completed, many=True).data

    def get_testimonials(self, obj):
        testimonials = Testimonial.objects.filter(
            is_active=True,
            is_deleted=False
        ).select_related('project').order_by('display_order', '-created_at')[:10]
        return TestimonialDisplaySerializer(testimonials, many=True).data


class PageHeroImagesSerializer(serializers.ModelSerializer):
    """Serializer for page hero images (Projects, About, Contact pages)."""
    
    def to_representation(self, instance):
        """Convert relative URLs to absolute URLs."""
        data = super().to_representation(instance)
        request = self.context.get('request')
        
        for field in ['projects_hero_image_url', 'about_hero_image_url', 'about_our_story_image_url', 'contact_hero_image_url']:
            url = data.get(field)
            if url and not url.startswith('http'):
                if request:
                    data[field] = request.build_absolute_uri(url)
                else:
                    from django.conf import settings
                    base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
                    data[field] = f"{base_url}{url}"
        
        return data

    class Meta:
        model = PageHeroImages
        fields = [
            'projects_hero_image_url',
            'about_hero_image_url',
            'about_our_story_image_url',
            'contact_hero_image_url'
        ]
