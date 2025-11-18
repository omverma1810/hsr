from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from django.utils import timezone
from .models import SystemStatus
from .permissions import IsAdminUser
from .utils import success_response, error_response
from rest_framework import status


class SessionInfoView(APIView):
    """Get current session information."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: OpenApiResponse(description='Session information retrieved successfully - Returns current session details including IP address, user agent, login time, and session status.'),
            401: OpenApiResponse(description='Unauthorized - Invalid or expired token.'),
        },
        description='''
        **Get Session Information**
        
        Retrieve detailed information about the current authenticated session.
        
        **Use Cases:**
        - Display session details in admin settings page
        - Security monitoring and auditing
        - Session management
        
        **Response includes:**
        - `login_time`: When the user logged in (ISO format)
        - `ip_address`: Client IP address (handles proxy headers)
        - `browser`: User agent string (browser/client information)
        - `user_agent`: Full user agent string
        - `status`: Current session status (Active)
        
        **Authentication Required:** Yes
        
        **Note:** This information helps track active sessions and can be used for security auditing. IP address detection handles X-Forwarded-For headers for proxy/load balancer scenarios.
        ''',
        examples=[
            OpenApiExample(
                'Success Response',
                value={
                    'success': True,
                    'message': 'Session information retrieved successfully',
                    'data': {
                        'login_time': '2024-01-15T10:30:00Z',
                        'ip_address': '127.0.0.1',
                        'browser': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
                        'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
                        'status': 'Active'
                    }
                },
                response_only=True
            )
        ],
        tags=['Authentication']
    )
    def get(self, request):
        try:
            user = request.user
            session_info = {
                'login_time': user.last_login.isoformat() if user.last_login else None,
                'ip_address': self.get_client_ip(request),
                'browser': request.META.get('HTTP_USER_AGENT', 'Unknown'),
                'user_agent': request.META.get('HTTP_USER_AGENT', 'Unknown'),
                'status': 'Active'
            }
            return success_response(
                data=session_info,
                message="Session information retrieved successfully"
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to retrieve session information"
            )
    
    def get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SystemSettingsView(APIView):
    """Get or update system settings."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(
        responses={
            200: OpenApiResponse(description='System settings retrieved successfully - Returns all system configuration including site name, URL, session timeout, maintenance mode, and notification settings.'),
            401: OpenApiResponse(description='Unauthorized - Invalid or expired token.'),
            403: OpenApiResponse(description='Forbidden - Admin access required.'),
        },
        description='''
        **Get System Settings**
        
        Retrieve all system-wide configuration settings.
        
        **Response includes:**
        - `site_name`: Website/brand name
        - `site_url`: Main website URL
        - `session_timeout`: Session timeout in minutes (default: 30)
        - `maintenance_mode`: Whether site is in maintenance mode
        - `auto_backup`: Whether automatic backups are enabled
        - `email_notifications`: Whether email notifications are enabled
        
        **Use Cases:**
        - Display system settings in admin panel
        - Configure site-wide behavior
        - Enable/disable maintenance mode
        
        **Authentication Required:** Yes (Admin only)
        ''',
        tags=['System Settings']
    )
    def get(self, request):
        try:
            system_status = SystemStatus.get_current()
            settings_data = {
                'site_name': getattr(system_status, 'site_name', 'HSR Green Homes'),
                'site_url': getattr(system_status, 'site_url', 'https://hsrgreenhomes.com'),
                'session_timeout': system_status.session_timeout if hasattr(system_status, 'session_timeout') else 30,
                'maintenance_mode': system_status.maintenance_mode if hasattr(system_status, 'maintenance_mode') else False,
                'auto_backup': getattr(system_status, 'auto_backup', False),
                'email_notifications': getattr(system_status, 'email_notifications', True),
            }
            return success_response(
                data=settings_data,
                message="System settings retrieved successfully"
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to retrieve system settings"
            )

    @extend_schema(
        request=dict,
        responses={
            200: OpenApiResponse(description='System settings updated successfully - All provided settings have been saved.'),
            400: OpenApiResponse(description='Validation error - Invalid field values provided.'),
            401: OpenApiResponse(description='Unauthorized - Invalid or expired token.'),
            403: OpenApiResponse(description='Forbidden - Admin access required.'),
        },
        description='''
        **Update System Settings**
        
        Update system-wide configuration settings.
        
        **Updatable Fields:**
        - `site_name` (string): Website/brand name
        - `site_url` (string): Main website URL
        - `session_timeout` (integer): Session timeout in minutes
        - `maintenance_mode` (boolean): Enable/disable maintenance mode
        - `auto_backup` (boolean): Enable/disable automatic backups
        - `email_notifications` (boolean): Enable/disable email notifications
        
        **Notes:**
        - Only send fields you want to update (partial updates supported)
        - All fields are optional
        - Changes take effect immediately
        - Maintenance mode affects public-facing endpoints
        
        **Authentication Required:** Yes (Admin only)
        ''',
        examples=[
            OpenApiExample(
                'Update System Settings Request',
                value={
                    'site_name': 'HSR Green Homes',
                    'site_url': 'https://hsrgreenhomes.com',
                    'session_timeout': 60,
                    'maintenance_mode': False,
                    'auto_backup': True,
                    'email_notifications': True
                },
                request_only=True
            )
        ],
        tags=['System Settings']
    )
    def put(self, request):
        try:
            system_status = SystemStatus.get_current()
            
            # Update allowed fields
            allowed_fields = ['site_name', 'site_url', 'session_timeout', 'maintenance_mode', 'auto_backup', 'email_notifications']
            for field in allowed_fields:
                if field in request.data:
                    setattr(system_status, field, request.data[field])
            
            system_status.save()
            
            settings_data = {
                'site_name': getattr(system_status, 'site_name', 'HSR Green Homes'),
                'site_url': getattr(system_status, 'site_url', 'https://hsrgreenhomes.com'),
                'session_timeout': system_status.session_timeout if hasattr(system_status, 'session_timeout') else 30,
                'maintenance_mode': system_status.maintenance_mode if hasattr(system_status, 'maintenance_mode') else False,
                'auto_backup': getattr(system_status, 'auto_backup', False),
                'email_notifications': getattr(system_status, 'email_notifications', True),
            }
            
            return success_response(
                data=settings_data,
                message="System settings updated successfully"
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to update system settings"
            )

