"""
Serializers for Contact Settings and System Configuration (Phase 6).
Handles contact information, system settings, and public contact API.
"""

from rest_framework import serializers
from .models import ContactSettings, SystemStatus


class WhatsAppConfigSerializer(serializers.Serializer):
    """Serializer for WhatsApp configuration."""
    whatsapp_enabled = serializers.BooleanField()
    whatsapp_number = serializers.CharField()
    whatsapp_business_hours = serializers.CharField()
    whatsapp_auto_reply = serializers.CharField()


class PhoneNumbersSerializer(serializers.Serializer):
    """Serializer for phone numbers configuration."""
    primary_phone = serializers.CharField()
    secondary_phone = serializers.CharField(allow_blank=True)
    toll_free_number = serializers.CharField(allow_blank=True)
    phone_business_hours = serializers.CharField()


class EmailSettingsSerializer(serializers.Serializer):
    """Serializer for email settings."""
    info_email = serializers.EmailField()
    sales_email = serializers.EmailField()
    support_email = serializers.EmailField()
    email_auto_reply_enabled = serializers.BooleanField()
    email_auto_reply_subject = serializers.CharField()
    email_auto_reply_message = serializers.CharField()


class AddressMapSerializer(serializers.Serializer):
    """Serializer for address and map configuration."""
    street_address = serializers.CharField()
    area_locality = serializers.CharField()
    city = serializers.CharField()
    state = serializers.CharField()
    pincode = serializers.CharField()
    country = serializers.CharField()
    google_maps_embed = serializers.CharField(allow_blank=True)
    full_address = serializers.SerializerMethodField()

    def get_full_address(self, obj):
        """Get formatted full address."""
        if hasattr(obj, 'get_full_address'):
            return obj.get_full_address()
        # For dict-like objects
        parts = [
            obj.get('street_address', ''),
            obj.get('area_locality', ''),
            obj.get('city', ''),
            obj.get('state', ''),
            obj.get('pincode', ''),
            obj.get('country', '')
        ]
        return ', '.join(filter(None, parts))


class SocialMediaSerializer(serializers.Serializer):
    """Serializer for social media links."""
    facebook_url = serializers.URLField(allow_blank=True)
    instagram_url = serializers.URLField(allow_blank=True)
    twitter_url = serializers.URLField(allow_blank=True)
    linkedin_url = serializers.URLField(allow_blank=True)
    youtube_url = serializers.URLField(allow_blank=True)


class ContactSettingsSerializer(serializers.ModelSerializer):
    """Complete contact settings serializer."""

    whatsapp_config = WhatsAppConfigSerializer(source='*', read_only=True)
    phone_numbers = PhoneNumbersSerializer(source='*', read_only=True)
    email_settings = EmailSettingsSerializer(source='*', read_only=True)
    address_map = AddressMapSerializer(source='*', read_only=True)
    social_media = SocialMediaSerializer(source='*', read_only=True)

    class Meta:
        model = ContactSettings
        fields = [
            'id',
            # WhatsApp
            'whatsapp_enabled', 'whatsapp_number', 'whatsapp_business_hours', 'whatsapp_auto_reply',
            # Phone
            'primary_phone', 'secondary_phone', 'toll_free_number', 'phone_business_hours',
            # Email
            'info_email', 'sales_email', 'support_email',
            'email_auto_reply_enabled', 'email_auto_reply_subject', 'email_auto_reply_message',
            # Address
            'street_address', 'area_locality', 'city', 'state', 'pincode', 'country', 'google_maps_embed',
            # Social Media
            'facebook_url', 'instagram_url', 'twitter_url', 'linkedin_url', 'youtube_url',
            # Nested representations
            'whatsapp_config', 'phone_numbers', 'email_settings', 'address_map', 'social_media',
            # Timestamps
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ContactSettingsUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating contact settings."""

    class Meta:
        model = ContactSettings
        fields = [
            # WhatsApp
            'whatsapp_enabled', 'whatsapp_number', 'whatsapp_business_hours', 'whatsapp_auto_reply',
            # Phone
            'primary_phone', 'secondary_phone', 'toll_free_number', 'phone_business_hours',
            # Email
            'info_email', 'sales_email', 'support_email',
            'email_auto_reply_enabled', 'email_auto_reply_subject', 'email_auto_reply_message',
            # Address
            'street_address', 'area_locality', 'city', 'state', 'pincode', 'country', 'google_maps_embed',
            # Social Media
            'facebook_url', 'instagram_url', 'twitter_url', 'linkedin_url', 'youtube_url',
        ]


class SystemStatusSerializer(serializers.ModelSerializer):
    """Serializer for system status and configuration."""

    uptime_status = serializers.SerializerMethodField()

    class Meta:
        model = SystemStatus
        fields = [
            'id',
            # Site Config
            'site_name', 'site_url',
            # System Health
            'website_status', 'whatsapp_integration_active', 'contact_forms_working',
            # Backup
            'last_backup_at', 'auto_backup_enabled',
            # Session
            'session_timeout',
            # Maintenance
            'maintenance_mode', 'maintenance_message',
            # Notifications
            'email_notifications_enabled', 'notification_email',
            # SEO
            'meta_title', 'meta_description', 'meta_keywords',
            # Computed
            'uptime_status',
            # Timestamps
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'last_backup_at', 'created_at', 'updated_at']

    def get_uptime_status(self, obj):
        """Return system uptime status."""
        return {
            'website': 'Online' if obj.website_status else 'Offline',
            'whatsapp': 'Active' if obj.whatsapp_integration_active else 'Inactive',
            'forms': 'Working' if obj.contact_forms_working else 'Not Working',
            'maintenance': 'Enabled' if obj.maintenance_mode else 'Disabled'
        }


class SystemStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating system status."""

    class Meta:
        model = SystemStatus
        fields = [
            'site_name', 'site_url',
            'website_status', 'whatsapp_integration_active', 'contact_forms_working',
            'auto_backup_enabled', 'session_timeout',
            'maintenance_mode', 'maintenance_message',
            'email_notifications_enabled', 'notification_email',
            'meta_title', 'meta_description', 'meta_keywords'
        ]


class TriggerBackupSerializer(serializers.Serializer):
    """Serializer for manual backup trigger."""
    message = serializers.CharField(read_only=True)
    timestamp = serializers.DateTimeField(read_only=True)


class PublicContactInfoSerializer(serializers.Serializer):
    """Public contact information (for frontend display)."""

    whatsapp = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    social_media = serializers.SerializerMethodField()

    def get_whatsapp(self, obj):
        if obj.whatsapp_enabled:
            return {
                'number': obj.whatsapp_number,
                'business_hours': obj.whatsapp_business_hours
            }
        return None

    def get_phone(self, obj):
        return {
            'primary': obj.primary_phone,
            'secondary': obj.secondary_phone if obj.secondary_phone else None,
            'toll_free': obj.toll_free_number if obj.toll_free_number else None,
            'business_hours': obj.phone_business_hours
        }

    def get_email(self, obj):
        return {
            'info': obj.info_email,
            'sales': obj.sales_email,
            'support': obj.support_email
        }

    def get_address(self, obj):
        return {
            'street': obj.street_address,
            'area': obj.area_locality,
            'city': obj.city,
            'state': obj.state,
            'pincode': obj.pincode,
            'country': obj.country,
            'full_address': obj.get_full_address(),
            'map_embed': obj.google_maps_embed if obj.google_maps_embed else None
        }

    def get_social_media(self, obj):
        return {
            'facebook': obj.facebook_url if obj.facebook_url else None,
            'instagram': obj.instagram_url if obj.instagram_url else None,
            'twitter': obj.twitter_url if obj.twitter_url else None,
            'linkedin': obj.linkedin_url if obj.linkedin_url else None,
            'youtube': obj.youtube_url if obj.youtube_url else None
        }
