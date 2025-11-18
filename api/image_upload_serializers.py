from rest_framework import serializers
from .models import UploadedImage


class UploadedImageSerializer(serializers.ModelSerializer):
    """Serializer for uploaded images."""
    
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = UploadedImage
        fields = ['id', 'title', 'image_url', 'description', 'uploaded_by', 'created_at', 'updated_at']
        read_only_fields = ['id', 'image_url', 'uploaded_by', 'created_at', 'updated_at']
    
    def get_image_url(self, obj):
        """Return the public URL for the image."""
        try:
            request = self.context.get('request')
            url = obj.get_image_url(request=request)
            # If image_url field is not set, set it now
            if url and not obj.image_url:
                try:
                    obj.image_url = url
                    obj.save(update_fields=['image_url'])
                except Exception:
                    # If save fails, just return the URL
                    pass
            return url or obj.image_url or ''
        except Exception:
            # Fallback to stored image_url if available
            return getattr(obj, 'image_url', '') or ''


class ImageUploadSerializer(serializers.Serializer):
    """Serializer for image upload requests."""
    
    image = serializers.ImageField(required=True, help_text='Image file to upload')
    title = serializers.CharField(required=False, allow_blank=True, max_length=255, help_text='Optional title for the image')
    description = serializers.CharField(required=False, allow_blank=True, help_text='Optional description for the image')
    
    def create(self, validated_data):
        """Create and save the uploaded image."""
        image_file = validated_data.pop('image')
        title = validated_data.get('title', '')
        description = validated_data.get('description', '')
        
        # Get the request from context to build absolute URL
        request = self.context.get('request')
        user = request.user if request and hasattr(request, 'user') else None
        
        # Create the UploadedImage instance
        uploaded_image = UploadedImage(
            image_file=image_file,
            title=title if title else None,
            description=description if description else None,
            uploaded_by=user
        )
        uploaded_image.save()
        
        # Generate and save the public URL
        if request:
            uploaded_image.image_url = request.build_absolute_uri(uploaded_image.image_file.url)
        else:
            from django.conf import settings
            base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
            uploaded_image.image_url = f"{base_url}{uploaded_image.image_file.url}"
        
        uploaded_image.save(update_fields=['image_url'])
        
        return uploaded_image

