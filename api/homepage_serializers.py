from rest_framework import serializers
from .models import HomePageContent, FeaturedProject, Project, Testimonial


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
    """Serializer for statistics section with structured output."""

    experience = serializers.SerializerMethodField()
    projects = serializers.SerializerMethodField()
    families = serializers.SerializerMethodField()
    sqft = serializers.SerializerMethodField()

    class Meta:
        model = HomePageContent
        fields = ['experience', 'projects', 'families', 'sqft']

    def get_experience(self, obj):
        return {
            'value': obj.stats_experience_value,
            'label': obj.stats_experience_label
        }

    def get_projects(self, obj):
        return {
            'value': obj.stats_projects_value,
            'label': obj.stats_projects_label
        }

    def get_families(self, obj):
        return {
            'value': obj.stats_families_value,
            'label': obj.stats_families_label
        }

    def get_sqft(self, obj):
        return {
            'value': obj.stats_sqft_value,
            'label': obj.stats_sqft_label
        }


class FooterInfoSerializer(serializers.ModelSerializer):
    """Serializer for footer information only."""

    class Meta:
        model = HomePageContent
        fields = [
            'footer_office_address',
            'footer_phone_number',
            'footer_email',
            'footer_whatsapp_number'
        ]


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

    class Meta:
        model = Project
        fields = [
            'id',
            'title',
            'location',
            'rera_number',
            'description',
            'status',
            'hero_image',
            'created_at'
        ]


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
    """Serializer for displaying testimonials on homepage."""

    project_title = serializers.CharField(source='project.title', read_only=True)
    project_location = serializers.CharField(source='project.location', read_only=True)

    class Meta:
        model = Testimonial
        fields = [
            'id',
            'customer_name',
            'project_title',
            'project_location',
            'quote',
            'customer_photo',
            'display_order'
        ]


class CompleteHomePageSerializer(serializers.Serializer):
    """
    Complete homepage data in a single optimized API call.
    Combines hero section, statistics, featured projects, and testimonials.
    """

    hero_section = serializers.SerializerMethodField()
    statistics = serializers.SerializerMethodField()
    footer = serializers.SerializerMethodField()
    featured_projects = serializers.SerializerMethodField()
    testimonials = serializers.SerializerMethodField()

    def get_hero_section(self, obj):
        return HeroSectionSerializer(obj).data

    def get_statistics(self, obj):
        return StatisticsSectionSerializer(obj).data

    def get_footer(self, obj):
        return FooterInfoSerializer(obj).data

    def get_featured_projects(self, obj):
        featured = FeaturedProject.objects.filter(
            is_active=True,
            project__is_deleted=False
        ).select_related('project').order_by('display_order')[:6]
        return FeaturedProjectSerializer(featured, many=True).data

    def get_testimonials(self, obj):
        testimonials = Testimonial.objects.filter(
            is_active=True,
            is_deleted=False
        ).select_related('project').order_by('display_order', '-created_at')[:10]
        return TestimonialDisplaySerializer(testimonials, many=True).data
