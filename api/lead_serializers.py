"""
Serializers for Lead Management (Phase 5).
Handles lead CRUD operations with priority, follow-ups, and conversion tracking.
"""

from rest_framework import serializers
from django.utils import timezone
from django.db.models import Q
from .models import Lead, Project, AdminUser


class LeadListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for lead list views."""

    project_title = serializers.CharField(source='project.title', read_only=True)
    project_location = serializers.CharField(source='project.location', read_only=True)
    contacted_by_name = serializers.CharField(source='contacted_by.full_name', read_only=True)
    status_color = serializers.CharField(source='get_status_display_color', read_only=True)
    priority_color = serializers.CharField(source='get_priority_display_color', read_only=True)
    time_ago = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = [
            'id',
            'name',
            'email',
            'phone',
            'project',
            'project_title',
            'project_location',
            'status',
            'status_color',
            'priority',
            'priority_color',
            'source',
            'preferred_contact_method',
            'next_follow_up',
            'follow_up_count',
            'contacted_at',
            'contacted_by_name',
            'time_ago',
            'is_overdue',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_time_ago(self, obj):
        """Calculate how long ago the lead was created."""
        now = timezone.now()
        diff = now - obj.created_at

        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds >= 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds >= 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"

    def get_is_overdue(self, obj):
        """Check if follow-up is overdue."""
        if obj.next_follow_up:
            return timezone.now() > obj.next_follow_up
        return False


class LeadDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual lead views."""

    project_title = serializers.CharField(source='project.title', read_only=True)
    project_location = serializers.CharField(source='project.location', read_only=True)
    contacted_by_name = serializers.CharField(source='contacted_by.full_name', read_only=True)
    contacted_by_email = serializers.EmailField(source='contacted_by.email', read_only=True)
    status_color = serializers.CharField(source='get_status_display_color', read_only=True)
    priority_color = serializers.CharField(source='get_priority_display_color', read_only=True)
    time_ago = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = [
            'id',
            'name',
            'email',
            'phone',
            'project',
            'project_title',
            'project_location',
            'message',
            'status',
            'status_color',
            'priority',
            'priority_color',
            'source',
            'preferred_contact_method',
            'next_follow_up',
            'follow_up_count',
            'contacted_at',
            'contacted_by',
            'contacted_by_name',
            'contacted_by_email',
            'notes',
            'time_ago',
            'is_overdue',
            'is_deleted',
            'deleted_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'deleted_at',
            'follow_up_count',
            'contacted_at',
        ]

    def get_time_ago(self, obj):
        """Calculate how long ago the lead was created."""
        now = timezone.now()
        diff = now - obj.created_at

        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds >= 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds >= 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"

    def get_is_overdue(self, obj):
        """Check if follow-up is overdue."""
        if obj.next_follow_up:
            return timezone.now() > obj.next_follow_up
        return False


class LeadCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new leads (public contact form)."""

    class Meta:
        model = Lead
        fields = [
            'name',
            'email',
            'phone',
            'project',
            'message',
            'source',
            'preferred_contact_method',
        ]

    def validate_name(self, value):
        """Validate name is not empty."""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Name must be at least 2 characters long."
            )
        return value

    def validate_message(self, value):
        """Validate message is not empty."""
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Message must be at least 10 characters long."
            )
        return value

    def validate_phone(self, value):
        """Validate phone number format."""
        # Remove spaces and special characters for validation
        cleaned = value.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        if not cleaned.replace('+', '').isdigit():
            raise serializers.ValidationError("Invalid phone number format.")
        return value


class LeadUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating existing leads (admin only)."""

    class Meta:
        model = Lead
        fields = [
            'name',
            'email',
            'phone',
            'project',
            'message',
            'status',
            'priority',
            'source',
            'preferred_contact_method',
            'next_follow_up',
            'notes',
        ]

    def validate_status(self, value):
        """Validate status is a valid choice."""
        valid_statuses = ['new', 'contacted', 'qualified', 'closed']
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        return value

    def validate_priority(self, value):
        """Validate priority is a valid choice."""
        valid_priorities = ['low', 'medium', 'high', 'urgent']
        if value not in valid_priorities:
            raise serializers.ValidationError(
                f"Invalid priority. Must be one of: {', '.join(valid_priorities)}"
            )
        return value


class LeadStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating lead status with automatic tracking."""

    status = serializers.ChoiceField(
        choices=['new', 'contacted', 'qualified', 'closed'],
        required=True
    )
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Optional notes about status change"
    )
    next_follow_up = serializers.DateTimeField(
        required=False,
        allow_null=True,
        help_text="Schedule next follow-up (optional)"
    )

    def validate_next_follow_up(self, value):
        """Validate next_follow_up is in the future."""
        if value and value < timezone.now():
            raise serializers.ValidationError(
                "Follow-up date must be in the future."
            )
        return value


class LeadAddNoteSerializer(serializers.Serializer):
    """Serializer for adding notes to a lead."""

    note = serializers.CharField(
        required=True,
        allow_blank=False,
        min_length=5,
        help_text="Note to add to the lead"
    )
    next_follow_up = serializers.DateTimeField(
        required=False,
        allow_null=True,
        help_text="Schedule next follow-up (optional)"
    )

    def validate_next_follow_up(self, value):
        """Validate next_follow_up is in the future."""
        if value and value < timezone.now():
            raise serializers.ValidationError(
                "Follow-up date must be in the future."
            )
        return value


class LeadStatisticsSerializer(serializers.Serializer):
    """Serializer for lead statistics and analytics."""

    total_leads = serializers.IntegerField()
    new_leads = serializers.IntegerField()
    contacted_leads = serializers.IntegerField()
    qualified_leads = serializers.IntegerField()
    closed_leads = serializers.IntegerField()

    # Conversion rates
    contact_rate = serializers.FloatField()
    qualification_rate = serializers.FloatField()
    close_rate = serializers.FloatField()

    # By priority
    urgent_leads = serializers.IntegerField()
    high_priority_leads = serializers.IntegerField()
    medium_priority_leads = serializers.IntegerField()
    low_priority_leads = serializers.IntegerField()

    # Follow-ups
    leads_with_follow_up = serializers.IntegerField()
    overdue_follow_ups = serializers.IntegerField()

    # By source
    source_breakdown = serializers.DictField()

    # Time-based
    leads_today = serializers.IntegerField()
    leads_this_week = serializers.IntegerField()
    leads_this_month = serializers.IntegerField()


class BulkLeadActionSerializer(serializers.Serializer):
    """Serializer for bulk actions on leads."""

    lead_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
        help_text="List of lead IDs to perform action on"
    )
    action = serializers.ChoiceField(
        choices=[
            'delete',
            'restore',
            'change_status',
            'change_priority',
            'assign_contact',
        ],
        help_text="Action to perform on selected leads"
    )
    status = serializers.ChoiceField(
        choices=['new', 'contacted', 'qualified', 'closed'],
        required=False,
        help_text="New status (required for change_status action)"
    )
    priority = serializers.ChoiceField(
        choices=['low', 'medium', 'high', 'urgent'],
        required=False,
        help_text="New priority (required for change_priority action)"
    )
    contacted_by = serializers.IntegerField(
        required=False,
        help_text="Admin user ID (required for assign_contact action)"
    )

    def validate_lead_ids(self, value):
        """Validate that lead IDs are provided."""
        if not value:
            raise serializers.ValidationError("At least one lead ID is required.")
        if len(value) > 100:
            raise serializers.ValidationError(
                "Cannot perform bulk action on more than 100 leads at once."
            )
        return value

    def validate(self, data):
        """Cross-field validation."""
        action = data.get('action')

        if action == 'change_status' and not data.get('status'):
            raise serializers.ValidationError({
                'status': 'Status is required for change_status action.'
            })

        if action == 'change_priority' and not data.get('priority'):
            raise serializers.ValidationError({
                'priority': 'Priority is required for change_priority action.'
            })

        if action == 'assign_contact' and not data.get('contacted_by'):
            raise serializers.ValidationError({
                'contacted_by': 'Admin user ID is required for assign_contact action.'
            })

        return data
