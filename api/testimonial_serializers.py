"""
Serializers for Testimonial Management (Phase 5).
Handles testimonial CRUD operations with ratings and verification.
"""

from rest_framework import serializers
from .models import Testimonial, Project


class TestimonialListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for testimonial list views."""

    project_title = serializers.CharField(source='project.title', read_only=True)
    project_location = serializers.CharField(source='project.location', read_only=True)
    rating_stars = serializers.CharField(source='get_rating_stars', read_only=True)

    class Meta:
        model = Testimonial
        fields = [
            'id',
            'customer_name',
            'project',
            'project_title',
            'project_location',
            'quote',
            'customer_photo',
            'rating',
            'rating_stars',
            'verified',
            'is_active',
            'display_order',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class TestimonialDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual testimonial views."""

    project_title = serializers.CharField(source='project.title', read_only=True)
    project_location = serializers.CharField(source='project.location', read_only=True)
    project_status = serializers.CharField(source='project.status', read_only=True)
    rating_stars = serializers.CharField(source='get_rating_stars', read_only=True)

    class Meta:
        model = Testimonial
        fields = [
            'id',
            'customer_name',
            'project',
            'project_title',
            'project_location',
            'project_status',
            'quote',
            'customer_photo',
            'rating',
            'rating_stars',
            'verified',
            'is_active',
            'display_order',
            'is_deleted',
            'deleted_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']


class TestimonialCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating testimonials."""

    class Meta:
        model = Testimonial
        fields = [
            'customer_name',
            'project',
            'quote',
            'customer_photo',
            'rating',
            'verified',
            'is_active',
            'display_order',
        ]

    def validate_rating(self, value):
        """Validate rating is between 1 and 5."""
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def validate_quote(self, value):
        """Validate quote is not empty and has minimum length."""
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Quote must be at least 10 characters long."
            )
        return value

    def validate_customer_name(self, value):
        """Validate customer name is not empty."""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Customer name must be at least 2 characters long."
            )
        return value


class BulkTestimonialActionSerializer(serializers.Serializer):
    """Serializer for bulk actions on testimonials."""

    testimonial_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
        help_text="List of testimonial IDs to perform action on"
    )
    action = serializers.ChoiceField(
        choices=['delete', 'restore', 'activate', 'deactivate', 'verify', 'unverify'],
        help_text="Action to perform on selected testimonials"
    )

    def validate_testimonial_ids(self, value):
        """Validate that testimonial IDs are provided."""
        if not value:
            raise serializers.ValidationError("At least one testimonial ID is required.")
        if len(value) > 100:
            raise serializers.ValidationError("Cannot perform bulk action on more than 100 testimonials at once.")
        return value
