from rest_framework import serializers
from .models import Lead, Project


class LeadSerializer(serializers.ModelSerializer):
    """Serializer for lead CRUD operations."""
    
    project_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    project_name = serializers.CharField(source='project.title', read_only=True)
    project_slug = serializers.CharField(source='project.slug', read_only=True)
    contacted_by_name = serializers.CharField(source='contacted_by.full_name', read_only=True)
    source_display = serializers.CharField(source='get_source_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Lead
        fields = [
            'id',
            'name',
            'email',
            'phone',
            'project_id',
            'project_name',
            'project_slug',
            'message',
            'source',
            'source_display',
            'status',
            'status_display',
            'contacted_at',
            'contacted_by',
            'contacted_by_name',
            'notes',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'contacted_at']
    
    def validate_project_id(self, value):
        """Validate that the project exists if provided."""
        if value is not None:
            try:
                Project.objects.get(id=value, is_deleted=False)
            except Project.DoesNotExist:
                raise serializers.ValidationError("Project not found or has been deleted.")
        return value
    
    def create(self, validated_data):
        """Create lead with project_id."""
        project_id = validated_data.pop('project_id', None)
        if project_id:
            validated_data['project'] = Project.objects.get(id=project_id, is_deleted=False)
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update lead with project_id if provided."""
        project_id = validated_data.pop('project_id', None)
        if project_id is not None:
            if project_id:
                validated_data['project'] = Project.objects.get(id=project_id, is_deleted=False)
            else:
                validated_data['project'] = None
        
        # Update contacted_at when status changes to contacted
        if 'status' in validated_data:
            if validated_data['status'] == 'contacted' and instance.status != 'contacted':
                from django.utils import timezone
                validated_data['contacted_at'] = timezone.now()
                if self.context.get('request') and self.context['request'].user:
                    validated_data['contacted_by'] = self.context['request'].user
        
        return super().update(instance, validated_data)


class LeadListSerializer(serializers.ModelSerializer):
    """Serializer for lead list view."""
    
    project_name = serializers.CharField(source='project.title', read_only=True)
    project_slug = serializers.CharField(source='project.slug', read_only=True)
    source_display = serializers.CharField(source='get_source_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Lead
        fields = [
            'id',
            'name',
            'email',
            'phone',
            'project_name',
            'project_slug',
            'message',
            'source',
            'source_display',
            'status',
            'status_display',
            'contacted_at',
            'created_at',
            'updated_at'
        ]

