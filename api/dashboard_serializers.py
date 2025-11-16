from rest_framework import serializers
from .models import Project, Lead, Testimonial, SystemStatus, AdminUser


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics."""
    total_projects = serializers.IntegerField()
    upcoming_projects = serializers.IntegerField()
    ongoing_projects = serializers.IntegerField()
    completed_projects = serializers.IntegerField()
    total_leads = serializers.IntegerField()
    new_leads = serializers.IntegerField()
    contacted_leads = serializers.IntegerField()
    qualified_leads = serializers.IntegerField()
    closed_leads = serializers.IntegerField()


class RecentLeadSerializer(serializers.ModelSerializer):
    """Serializer for recent leads display."""
    project_name = serializers.CharField(source='project.title', read_only=True)
    time_ago = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = ['id', 'name', 'email', 'phone', 'project_name', 'message', 'status', 'created_at', 'time_ago']

    def get_time_ago(self, obj):
        """Calculate time ago in human-readable format."""
        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()
        diff = now - obj.created_at

        if diff < timedelta(minutes=1):
            return "just now"
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff < timedelta(days=7):
            days = diff.days
            return f"{days} day{'s' if days > 1 else ''} ago"
        else:
            return obj.created_at.strftime("%b %d, %Y")


class SystemStatusSerializer(serializers.ModelSerializer):
    """Serializer for system status."""
    website_status_display = serializers.SerializerMethodField()
    whatsapp_status_display = serializers.SerializerMethodField()
    contact_forms_display = serializers.SerializerMethodField()
    last_backup_display = serializers.SerializerMethodField()

    class Meta:
        model = SystemStatus
        fields = [
            'website_status', 'website_status_display',
            'whatsapp_integration_active', 'whatsapp_status_display',
            'contact_forms_working', 'contact_forms_display',
            'last_backup_at', 'last_backup_display',
            'maintenance_mode', 'session_timeout'
        ]

    def get_website_status_display(self, obj):
        return "Online" if obj.website_status else "Offline"

    def get_whatsapp_status_display(self, obj):
        return "Active" if obj.whatsapp_integration_active else "Inactive"

    def get_contact_forms_display(self, obj):
        return "Working" if obj.contact_forms_working else "Not Working"

    def get_last_backup_display(self, obj):
        from django.utils import timezone
        if obj.last_backup_at:
            now = timezone.now()
            if obj.last_backup_at.date() == now.date():
                return obj.last_backup_at.strftime("Today, %I:%M %p")
            else:
                return obj.last_backup_at.strftime("%b %d, %I:%M %p")
        return "Never"


class ProjectStatusBreakdownSerializer(serializers.Serializer):
    """Serializer for project status breakdown."""
    status = serializers.CharField()
    count = serializers.IntegerField()
    percentage = serializers.FloatField()


class LeadStatusBreakdownSerializer(serializers.Serializer):
    """Serializer for lead status breakdown."""
    status = serializers.CharField()
    count = serializers.IntegerField()
    percentage = serializers.FloatField()


class DashboardOverviewSerializer(serializers.Serializer):
    """Complete dashboard overview serializer."""
    statistics = DashboardStatsSerializer()
    recent_leads = RecentLeadSerializer(many=True)
    system_status = SystemStatusSerializer()
    project_breakdown = ProjectStatusBreakdownSerializer(many=True)
    lead_breakdown = LeadStatusBreakdownSerializer(many=True)
