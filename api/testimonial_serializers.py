from rest_framework import serializers
from .models import Testimonial, Project


class TestimonialSerializer(serializers.ModelSerializer):
    """Serializer for testimonial CRUD operations."""
    
    project_id = serializers.IntegerField(write_only=True, required=False)
    project_title = serializers.CharField(source='project.title', read_only=True)
    project_location = serializers.CharField(source='project.location', read_only=True)
    
    class Meta:
        model = Testimonial
        fields = [
            'id',
            'customer_name',
            'project_id',
            'project_title',
            'project_location',
            'quote',
            'customer_photo',
            'is_active',
            'display_order',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        """Add project_id to read response."""
        ret = super().to_representation(instance)
        ret['project_id'] = instance.project.id if instance.project else None
        return ret
    
    def validate_project_id(self, value):
        """Validate that the project exists and is not deleted."""
        if value is None or value == 0:
            raise serializers.ValidationError("Project is required.")
        try:
            project = Project.objects.get(id=value, is_deleted=False)
            return value
        except Project.DoesNotExist:
            raise serializers.ValidationError("Project not found or has been deleted.")
    
    def create(self, validated_data):
        """Create testimonial with project_id."""
        project_id = validated_data.pop('project_id', None)
        if not project_id or project_id == 0:
            raise serializers.ValidationError({"project_id": "Project is required."})
        project = Project.objects.get(id=project_id, is_deleted=False)
        validated_data['project'] = project
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update testimonial with project_id if provided."""
        if 'project_id' in validated_data:
            project_id = validated_data.pop('project_id')
            if not project_id or project_id == 0:
                raise serializers.ValidationError({"project_id": "Project is required."})
            project = Project.objects.get(id=project_id, is_deleted=False)
            validated_data['project'] = project
        return super().update(instance, validated_data)


class TestimonialListSerializer(serializers.ModelSerializer):
    """Serializer for testimonial list view."""
    
    project_id = serializers.IntegerField(source='project.id', read_only=True)
    project_title = serializers.CharField(source='project.title', read_only=True)
    project_location = serializers.CharField(source='project.location', read_only=True)
    
    class Meta:
        model = Testimonial
        fields = [
            'id',
            'customer_name',
            'project_id',
            'project_title',
            'project_location',
            'quote',
            'customer_photo',
            'is_active',
            'display_order',
            'created_at',
            'updated_at'
        ]

