from rest_framework import serializers
from .models import ContactSettings


class ContactSettingsSerializer(serializers.ModelSerializer):
    """Serializer for contact settings."""
    
    # Override URL fields to allow empty strings
    facebook_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    instagram_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    twitter_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    linkedin_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    youtube_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    
    def validate_facebook_url(self, value):
        """Validate Facebook URL format."""
        if value and value.strip():
            if not value.startswith(('http://', 'https://')):
                raise serializers.ValidationError("URL must start with http:// or https://")
            if 'facebook.com' not in value.lower():
                raise serializers.ValidationError("Please enter a valid Facebook URL (e.g., https://www.facebook.com/yourpage)")
        return value.strip() if value else None
    
    def validate_instagram_url(self, value):
        """Validate Instagram URL format."""
        if value and value.strip():
            if not value.startswith(('http://', 'https://')):
                raise serializers.ValidationError("URL must start with http:// or https://")
            if 'instagram.com' not in value.lower():
                raise serializers.ValidationError("Please enter a valid Instagram URL (e.g., https://www.instagram.com/yourprofile)")
        return value.strip() if value else None
    
    def validate_twitter_url(self, value):
        """Validate Twitter URL format."""
        if value and value.strip():
            if not value.startswith(('http://', 'https://')):
                raise serializers.ValidationError("URL must start with http:// or https://")
            if 'twitter.com' not in value.lower() and 'x.com' not in value.lower():
                raise serializers.ValidationError("Please enter a valid Twitter/X URL (e.g., https://twitter.com/yourprofile)")
        return value.strip() if value else None
    
    def validate_linkedin_url(self, value):
        """Validate LinkedIn URL format."""
        if value and value.strip():
            if not value.startswith(('http://', 'https://')):
                raise serializers.ValidationError("URL must start with http:// or https://")
            if 'linkedin.com' not in value.lower():
                raise serializers.ValidationError("Please enter a valid LinkedIn URL (e.g., https://www.linkedin.com/company/yourcompany)")
        return value.strip() if value else None
    
    def validate_youtube_url(self, value):
        """Validate YouTube URL format."""
        if value and value.strip():
            if not value.startswith(('http://', 'https://')):
                raise serializers.ValidationError("URL must start with http:// or https://")
            if 'youtube.com' not in value.lower() and 'youtu.be' not in value.lower():
                raise serializers.ValidationError("Please enter a valid YouTube URL (e.g., https://www.youtube.com/@yourchannel)")
        return value.strip() if value else None
    
    class Meta:
        model = ContactSettings
        fields = [
            # WhatsApp
            'whatsapp_enabled',
            'whatsapp_number',
            'whatsapp_business_hours',
            'whatsapp_auto_reply',
            # Phone
            'primary_phone',
            'secondary_phone',
            'toll_free_number',
            'phone_business_hours',
            # Email
            'info_email',
            'sales_email',
            'support_email',
            'email_auto_reply_enabled',
            'email_auto_reply_subject',
            'email_auto_reply_message',
            # Address
            'street_address',
            'area',
            'city',
            'state',
            'pincode',
            'country',
            'google_maps_embed_code',
            # Social Media
            'facebook_url',
            'instagram_url',
            'twitter_url',
            'linkedin_url',
            'youtube_url',
            # Timestamps
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

