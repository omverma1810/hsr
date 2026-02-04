from rest_framework import serializers
from .models import Award

class AwardSerializer(serializers.ModelSerializer):
    """Serializer for Award model."""
    image = serializers.SerializerMethodField()
    image_file = serializers.ImageField(required=False, allow_null=True, write_only=True)
    image_url = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    is_active = serializers.BooleanField(required=False, default=True)

    class Meta:
        model = Award
        fields = ['id', 'title', 'description', 'image_url', 'image_file', 'image', 'display_order', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'image']

    def to_internal_value(self, data):
        """Handle FormData where is_active comes as string 'true'/'false'."""
        # Convert mutable copy
        if hasattr(data, 'copy'):
            data = data.copy()
        
        # Handle is_active string -> boolean conversion
        if 'is_active' in data:
            val = data.get('is_active')
            if isinstance(val, str):
                data['is_active'] = val.lower() in ('true', '1', 'yes')
        
        return super().to_internal_value(data)

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

