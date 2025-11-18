from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema
from .models import ContactSettings
from .contact_serializers import ContactSettingsSerializer
from .permissions import IsAdminUser
from .utils import success_response, error_response
from rest_framework import status


class ContactSettingsView(APIView):
    """Get or update contact settings."""
    
    # Allow public access for GET, require auth for PUT
    permission_classes = [AllowAny]
    
    @extend_schema(
        responses={200: ContactSettingsSerializer},
        description="Get contact settings (public access for website, admin access for management)"
    )
    def get(self, request):
        """Get contact settings. Public access for website display."""
        try:
            settings = ContactSettings.get_current()
            serializer = ContactSettingsSerializer(settings)
            return success_response(
                data=serializer.data,
                message="Contact settings retrieved successfully"
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to retrieve contact settings"
            )
    
    @extend_schema(
        request=ContactSettingsSerializer,
        responses={200: ContactSettingsSerializer},
        description="Update contact settings (admin only)"
    )
    def put(self, request):
        """Update contact settings. Admin only."""
        # Check permissions for PUT method
        if not (request.user and request.user.is_staff):
            return error_response(
                errors={'detail': 'Permission denied'},
                message="Admin access required",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        try:
            settings = ContactSettings.get_current()
            serializer = ContactSettingsSerializer(settings, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return success_response(
                    data=serializer.data,
                    message="Contact settings updated successfully"
                )
            
            return error_response(
                errors=serializer.errors,
                message="Failed to update contact settings"
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to update contact settings"
            )

