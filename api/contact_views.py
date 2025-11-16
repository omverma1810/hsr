"""
Views for Contact Settings and System Configuration (Phase 6).
Handles contact information management and system status.
"""

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.utils import timezone

from .models import ContactSettings, SystemStatus
from .contact_serializers import (
    ContactSettingsSerializer,
    ContactSettingsUpdateSerializer,
    WhatsAppConfigSerializer,
    PhoneNumbersSerializer,
    EmailSettingsSerializer,
    AddressMapSerializer,
    SocialMediaSerializer,
    SystemStatusSerializer,
    SystemStatusUpdateSerializer,
    TriggerBackupSerializer,
    PublicContactInfoSerializer
)
from .utils import success_response, error_response
from .permissions import IsAdminUser


class ContactSettingsView(APIView):
    """
    Get or update complete contact settings.
    GET: Public access for contact information
    PUT: Admin only for settings management
    """

    def get_permissions(self):
        """Public GET, admin PUT."""
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]

    def get(self, request):
        """Get current contact settings."""
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
                message="Failed to retrieve contact settings",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request):
        """Update contact settings."""
        try:
            settings = ContactSettings.get_current()
            serializer = ContactSettingsUpdateSerializer(
                settings,
                data=request.data,
                partial=True
            )

            if serializer.is_valid():
                serializer.save()
                response_serializer = ContactSettingsSerializer(settings)

                return success_response(
                    data=response_serializer.data,
                    message="Contact settings updated successfully"
                )

            return error_response(
                errors=serializer.errors,
                message="Failed to update contact settings",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to update contact settings",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WhatsAppConfigView(APIView):
    """Get or update WhatsApp configuration."""

    def get_permissions(self):
        """Public GET, admin PUT."""
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]

    def get(self, request):
        """Get WhatsApp configuration."""
        try:
            settings = ContactSettings.get_current()
            serializer = WhatsAppConfigSerializer(settings)

            return success_response(
                data=serializer.data,
                message="WhatsApp configuration retrieved successfully"
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to retrieve WhatsApp configuration",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request):
        """Update WhatsApp configuration."""
        try:
            settings = ContactSettings.get_current()

            # Update WhatsApp fields
            if 'whatsapp_enabled' in request.data:
                settings.whatsapp_enabled = request.data['whatsapp_enabled']
            if 'whatsapp_number' in request.data:
                settings.whatsapp_number = request.data['whatsapp_number']
            if 'whatsapp_business_hours' in request.data:
                settings.whatsapp_business_hours = request.data['whatsapp_business_hours']
            if 'whatsapp_auto_reply' in request.data:
                settings.whatsapp_auto_reply = request.data['whatsapp_auto_reply']

            settings.save()
            serializer = WhatsAppConfigSerializer(settings)

            return success_response(
                data=serializer.data,
                message="WhatsApp configuration updated successfully"
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to update WhatsApp configuration",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PhoneNumbersView(APIView):
    """Get or update phone numbers configuration."""

    def get_permissions(self):
        """Public GET, admin PUT."""
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]

    def get(self, request):
        """Get phone numbers."""
        try:
            settings = ContactSettings.get_current()
            serializer = PhoneNumbersSerializer(settings)

            return success_response(
                data=serializer.data,
                message="Phone numbers retrieved successfully"
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to retrieve phone numbers",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request):
        """Update phone numbers."""
        try:
            settings = ContactSettings.get_current()

            # Update phone fields
            if 'primary_phone' in request.data:
                settings.primary_phone = request.data['primary_phone']
            if 'secondary_phone' in request.data:
                settings.secondary_phone = request.data['secondary_phone']
            if 'toll_free_number' in request.data:
                settings.toll_free_number = request.data['toll_free_number']
            if 'phone_business_hours' in request.data:
                settings.phone_business_hours = request.data['phone_business_hours']

            settings.save()
            serializer = PhoneNumbersSerializer(settings)

            return success_response(
                data=serializer.data,
                message="Phone numbers updated successfully"
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to update phone numbers",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EmailSettingsView(APIView):
    """Get or update email settings."""

    def get_permissions(self):
        """Public GET, admin PUT."""
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]

    def get(self, request):
        """Get email settings."""
        try:
            settings = ContactSettings.get_current()
            serializer = EmailSettingsSerializer(settings)

            return success_response(
                data=serializer.data,
                message="Email settings retrieved successfully"
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to retrieve email settings",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request):
        """Update email settings."""
        try:
            settings = ContactSettings.get_current()

            # Update email fields
            email_fields = [
                'info_email', 'sales_email', 'support_email',
                'email_auto_reply_enabled', 'email_auto_reply_subject', 'email_auto_reply_message'
            ]

            for field in email_fields:
                if field in request.data:
                    setattr(settings, field, request.data[field])

            settings.save()
            serializer = EmailSettingsSerializer(settings)

            return success_response(
                data=serializer.data,
                message="Email settings updated successfully"
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to update email settings",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AddressMapView(APIView):
    """Get or update address and map configuration."""

    def get_permissions(self):
        """Public GET, admin PUT."""
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]

    def get(self, request):
        """Get address and map."""
        try:
            settings = ContactSettings.get_current()
            serializer = AddressMapSerializer(settings)

            return success_response(
                data=serializer.data,
                message="Address and map retrieved successfully"
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to retrieve address and map",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request):
        """Update address and map."""
        try:
            settings = ContactSettings.get_current()

            # Update address fields
            address_fields = [
                'street_address', 'area_locality', 'city', 'state',
                'pincode', 'country', 'google_maps_embed'
            ]

            for field in address_fields:
                if field in request.data:
                    setattr(settings, field, request.data[field])

            settings.save()
            serializer = AddressMapSerializer(settings)

            return success_response(
                data=serializer.data,
                message="Address and map updated successfully"
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to update address and map",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SocialMediaView(APIView):
    """Get or update social media links."""

    def get_permissions(self):
        """Public GET, admin PUT."""
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]

    def get(self, request):
        """Get social media links."""
        try:
            settings = ContactSettings.get_current()
            serializer = SocialMediaSerializer(settings)

            return success_response(
                data=serializer.data,
                message="Social media links retrieved successfully"
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to retrieve social media links",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request):
        """Update social media links."""
        try:
            settings = ContactSettings.get_current()

            # Update social media fields
            social_fields = [
                'facebook_url', 'instagram_url', 'twitter_url',
                'linkedin_url', 'youtube_url'
            ]

            for field in social_fields:
                if field in request.data:
                    setattr(settings, field, request.data[field])

            settings.save()
            serializer = SocialMediaSerializer(settings)

            return success_response(
                data=serializer.data,
                message="Social media links updated successfully"
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to update social media links",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PublicContactInfoView(APIView):
    """Get public contact information (optimized for frontend)."""
    permission_classes = [AllowAny]

    def get(self, request):
        """Get public contact info."""
        try:
            settings = ContactSettings.get_current()
            serializer = PublicContactInfoSerializer(settings)

            return success_response(
                data=serializer.data,
                message="Public contact information retrieved successfully"
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to retrieve contact information",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SystemStatusView(APIView):
    """Get or update system status and configuration."""

    def get_permissions(self):
        """Public GET (limited info), admin PUT."""
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]

    def get(self, request):
        """Get system status."""
        try:
            system_status = SystemStatus.get_current()
            serializer = SystemStatusSerializer(system_status)

            # Filter sensitive data for non-admin users
            data = serializer.data
            if not (request.user.is_authenticated and request.user.is_staff):
                # Public users only see basic status
                data = {
                    'site_name': data['site_name'],
                    'maintenance_mode': data['maintenance_mode'],
                    'maintenance_message': data['maintenance_message'] if data['maintenance_mode'] else None
                }

            return success_response(
                data=data,
                message="System status retrieved successfully"
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to retrieve system status",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request):
        """Update system status."""
        try:
            system_status = SystemStatus.get_current()
            serializer = SystemStatusUpdateSerializer(
                system_status,
                data=request.data,
                partial=True
            )

            if serializer.is_valid():
                serializer.save()
                response_serializer = SystemStatusSerializer(system_status)

                return success_response(
                    data=response_serializer.data,
                    message="System status updated successfully"
                )

            return error_response(
                errors=serializer.errors,
                message="Failed to update system status",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to update system status",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TriggerBackupView(APIView):
    """Manually trigger a system backup."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        """Trigger backup."""
        try:
            system_status = SystemStatus.get_current()
            system_status.trigger_backup()

            data = {
                'message': 'Backup triggered successfully',
                'timestamp': system_status.last_backup_at
            }

            return success_response(
                data=data,
                message="Backup triggered successfully"
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to trigger backup",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
