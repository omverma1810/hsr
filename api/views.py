from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from django.utils import timezone
from django.conf import settings
from django.db import connection
from django import get_version as get_django_version
from .serializers import LoginSerializer, AdminUserSerializer, ChangePasswordSerializer, ResetPasswordSerializer
from .utils import success_response, error_response
from .permissions import IsAdminUser


class LoginView(APIView):
    """API endpoint for admin user login."""
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(description='Login successful - Returns user details and JWT tokens (access & refresh). Note: All previous tokens for this user are automatically blacklisted to enforce single active session.'),
            400: OpenApiResponse(description='Invalid credentials - Email or password is incorrect, or user account is disabled.'),
        },
        description='''
        **Admin User Login**
        
        Authenticate an admin user and receive JWT access and refresh tokens.
        
        **Important Notes:**
        - On successful login, all previous tokens for this user are blacklisted
        - This enforces single active session - if user logs in from Swagger, their frontend session will be invalidated
        - Store both `access` and `refresh` tokens securely
        - Access token is used for API requests (add to Authorization header: `Bearer <access_token>`)
        - Refresh token is used to get new access tokens when they expire
        
        **Request Body:**
        - `email`: Admin user email address
        - `password`: User password
        
        **Response:**
        - `user`: User details (id, email, full_name, role, is_staff)
        - `tokens.access`: JWT access token (short-lived, ~60 minutes)
        - `tokens.refresh`: JWT refresh token (long-lived, ~7 days)
        ''',
        examples=[
            OpenApiExample(
                'Login Request',
                value={
                    'email': 'admin@example.com',
                    'password': 'your-password'
                },
                request_only=True
            ),
            OpenApiExample(
                'Success Response',
                value={
                    'success': True,
                    'message': 'Login successful',
                    'data': {
                        'user': {
                            'id': 1,
                            'email': 'admin@example.com',
                            'full_name': 'Admin User',
                            'role': 'admin',
                            'is_staff': True
                        },
                        'tokens': {
                            'access': 'eyJ0eXAiOiJKV1QiLCJhbGc...',
                            'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGc...'
                        }
                    }
                },
                response_only=True
            )
        ],
        tags=['Authentication']
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Blacklist all previous tokens for this user (single session enforcement)
            # This ensures that when user logs in from another location (e.g., Swagger),
            # the previous session (e.g., localhost frontend) will be invalidated
            try:
                outstanding_tokens = OutstandingToken.objects.filter(user=user)
                for token in outstanding_tokens:
                    try:
                        refresh_token = RefreshToken(token.token)
                        refresh_token.blacklist()
                    except Exception:
                        # Token might already be blacklisted or invalid, skip it
                        pass
            except Exception:
                # If blacklist functionality is not available, continue anyway
                pass
            
            # Create new tokens for this login
            refresh = RefreshToken.for_user(user)

            return success_response(
                data={
                    'user': AdminUserSerializer(user).data,
                    'tokens': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                    }
                },
                message='Login successful',
                status_code=status.HTTP_200_OK
            )

        return error_response(
            errors=serializer.errors,
            message='Login failed',
            status_code=status.HTTP_400_BAD_REQUEST
        )


class LogoutView(APIView):
    """API endpoint for admin user logout."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={'refresh': 'string'},
        responses={
            200: OpenApiResponse(description='Logout successful - Refresh token has been blacklisted. User must login again to access protected endpoints.'),
            400: OpenApiResponse(description='Invalid token - Refresh token is missing, invalid, or already blacklisted.'),
        },
        description='''
        **User Logout**
        
        Logout the current user by blacklisting their refresh token.
        
        **How it works:**
        - Blacklists the refresh token so it cannot be used to get new access tokens
        - User will need to login again to get new tokens
        - Access token remains valid until it expires (cannot be immediately invalidated)
        
        **Request Body:**
        - `refresh`: The refresh token to blacklist
        
        **Note:** After logout, clear tokens from client-side storage and redirect to login page.
        ''',
        examples=[
            OpenApiExample(
                'Logout Request',
                value={
                    'refresh': 'your-refresh-token-here'
                },
                request_only=True
            )
        ],
        tags=['Authentication']
    )
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return error_response(
                    errors={'refresh': 'Refresh token is required'},
                    message='Logout failed',
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            return success_response(
                message='Logout successful',
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message='Logout failed',
                status_code=status.HTTP_400_BAD_REQUEST
            )


class CurrentUserView(APIView):
    """API endpoint to get current authenticated user details."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: OpenApiResponse(description='User details retrieved successfully - Returns current authenticated user information including id, email, full_name, role, and is_staff status.'),
            401: OpenApiResponse(description='Unauthorized - Invalid or expired token. Use /auth/refresh/ to get new tokens.'),
        },
        description='''
        **Get Current User**
        
        Retrieve details of the currently authenticated user.
        
        **Use Cases:**
        - Display user information in admin panel
        - Verify authentication status
        - Check user permissions
        
        **Response includes:**
        - User ID, email, full name
        - Role and staff status
        - Last login timestamp
        - Account creation date
        
        **Authentication Required:** Yes (Bearer token in Authorization header)
        ''',
        tags=['Authentication']
    )
    def get(self, request):
        serializer = AdminUserSerializer(request.user)
        return success_response(
            data=serializer.data,
            message='User details retrieved successfully',
            status_code=status.HTTP_200_OK
        )

    @extend_schema(
        request=AdminUserSerializer,
        responses={
            200: OpenApiResponse(description='Account updated successfully - User information has been updated.'),
            400: OpenApiResponse(description='Validation error - Check errors object for field-specific issues (e.g., invalid email format).'),
        },
        description='''
        **Update Current User Account**
        
        Update your own account information (full name, email).
        
        **Updatable Fields:**
        - `full_name`: Your display name
        - `email`: Your email address (must be unique)
        
        **Read-only Fields (cannot be changed):**
        - `id`, `role`, `is_staff`, `last_login`, `date_joined`
        
        **Notes:**
        - Email must be unique across all users
        - Changes take effect immediately
        - Use PATCH for partial updates (only send fields you want to change)
        
        **Authentication Required:** Yes
        ''',
        examples=[
            OpenApiExample(
                'Update Account Request',
                value={
                    'full_name': 'Updated Name',
                    'email': 'newemail@example.com'
                },
                request_only=True
            )
        ],
        tags=['Authentication']
    )
    def put(self, request):
        """Update current user account information."""
        serializer = AdminUserSerializer(request.user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return success_response(
                data=serializer.data,
                message='Account updated successfully',
                status_code=status.HTTP_200_OK
            )
        
        return error_response(
            errors=serializer.errors,
            message='Failed to update account',
            status_code=status.HTTP_400_BAD_REQUEST
        )


class ChangePasswordView(APIView):
    """API endpoint to change user password."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ChangePasswordSerializer,
        responses={
            200: OpenApiResponse(description='Password changed successfully - Your password has been updated. Use new password for future logins.'),
            400: OpenApiResponse(description='Validation errors - Current password incorrect, passwords do not match, or new password does not meet complexity requirements.'),
        },
        description='''
        **Change Password**
        
        Change your password while logged in (requires current password).
        
        **Password Requirements:**
        - At least 8 characters long
        - At least one uppercase letter (A-Z)
        - At least one lowercase letter (a-z)
        - At least one number (0-9)
        - At least one special character (!@#$%^&*(),.?":{}|<>)
        
        **Request Body:**
        - `current_password`: Your current password (for verification)
        - `new_password`: Your new password (must meet requirements above)
        - `confirm_password`: Must match `new_password` exactly
        
        **Security Notes:**
        - Current password is verified before allowing change
        - New password must be different from current password
        - After password change, you may need to login again with new password
        
        **Authentication Required:** Yes
        ''',
        examples=[
            OpenApiExample(
                'Change Password Request',
                value={
                    'current_password': 'OldPassword123!',
                    'new_password': 'NewPassword456!',
                    'confirm_password': 'NewPassword456!'
                },
                request_only=True
            )
        ],
        tags=['Authentication']
    )
    def put(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return success_response(
                message='Password changed successfully',
                status_code=status.HTTP_200_OK
            )

        return error_response(
            errors=serializer.errors,
            message='Password change failed',
            status_code=status.HTTP_400_BAD_REQUEST
        )


class ResetPasswordView(APIView):
    """API endpoint to reset password without current password (for forgot password flow)."""
    permission_classes = [AllowAny]

    @extend_schema(
        request=ResetPasswordSerializer,
        responses={
            200: OpenApiResponse(description='Password reset successfully - You can now login with your new password.'),
            400: OpenApiResponse(description='Validation errors - Email not found, passwords do not match, or new password does not meet complexity requirements.'),
        },
        description='''
        **Reset Password (Forgot Password)**
        
        Reset password without knowing current password (for forgot password flow).
        
        **Use Case:**
        - User forgot their password
        - User needs to reset password without being logged in
        
        **How it works:**
        - Requires email address of admin user
        - Validates that email exists and belongs to an admin account
        - Sets new password if validation passes
        
        **Password Requirements:**
        - At least 8 characters long
        - At least one uppercase letter (A-Z)
        - At least one lowercase letter (a-z)
        - At least one number (0-9)
        - At least one special character (!@#$%^&*(),.?":{}|<>)
        
        **Request Body:**
        - `email`: Admin user email address (must exist and be admin account)
        - `new_password`: New password (must meet requirements)
        - `confirm_password`: Must match `new_password` exactly
        
        **Security Note:** This endpoint is public but only works for admin accounts. After reset, user must login with new password.
        
        **Authentication Required:** No (Public endpoint)
        ''',
        examples=[
            OpenApiExample(
                'Reset Password Request',
                value={
                    'email': 'admin@example.com',
                    'new_password': 'NewSecurePassword123!',
                    'confirm_password': 'NewSecurePassword123!'
                },
                request_only=True
            )
        ],
        tags=['Authentication']
    )
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return success_response(
                message='Password reset successfully. You can now login with your new password.',
                status_code=status.HTTP_200_OK
            )

        return error_response(
            errors=serializer.errors,
            message='Password reset failed',
            status_code=status.HTTP_400_BAD_REQUEST
        )


class DevIndexView(APIView):
    """Simple root endpoint for development.

    Returns a JSON listing of useful development endpoints (admin, api docs,
    schema) so that opening http://127.0.0.1:8000/ in a browser will show that
    the server is running and where to find API docs.
    """
    permission_classes = [AllowAny]

    # Support both HTML (default in browsers) and JSON (curl, scripts)
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'api/dev_index.html'

    def get(self, request):
        data = {
            'message': 'Development server is running',
            'endpoints': {
                'admin': request.build_absolute_uri('/admin/'),
                'api_root': request.build_absolute_uri('/api/'),
                'swagger_ui': request.build_absolute_uri('/api/docs/'),
                'redoc': request.build_absolute_uri('/api/redoc/'),
                'schema': request.build_absolute_uri('/api/schema/'),
            },
            'tip': 'Use browser JSON pretty print or the Swagger UI to explore the API',
        }

        # If the client accepts HTML, DRF will render the template
        return Response(data, template_name=self.template_name)


# Save the service start time so uptime can be calculated
SERVICE_START_TIME = timezone.now()


class PingView(APIView):
    """Health-check endpoint for quick verification.

    GET /api/ping/ -> {'status': 'ok', 'message': 'pong'}
    """
    permission_classes = [AllowAny]

    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'api/ping.html'

    @extend_schema(
        responses={
            200: OpenApiResponse(description='API is alive and database connection is healthy - Returns status, database connection status, uptime, version, and timestamp.'),
            503: OpenApiResponse(description='Service unavailable - Database connection failed.'),
        },
        description='''
        **Health Check (Ping)**
        
        Simple endpoint to check API liveness and database connectivity.
        
        **Use Cases:**
        - Health monitoring
        - Load balancer health checks
        - System status verification
        - Development testing
        
        **Response includes:**
        - `status`: API status (usually "ok")
        - `message`: Response message ("pong")
        - `db`: Database connection status ("ok" or error message)
        - `uptime_seconds`: Server uptime in seconds
        - `version`: Application/Django version
        - `timestamp`: Current server timestamp (ISO format)
        - `api_root`: Base API URL
        
        **Note:** This endpoint is public and does not require authentication. It's useful for monitoring and debugging.
        
        **Authentication Required:** No (Public endpoint)
        ''',
        tags=['Health Check']
    )
    def get(self, request):
        now = timezone.now()
        uptime_delta = now - SERVICE_START_TIME
        uptime_seconds = int(uptime_delta.total_seconds())

        # Basic DB health check
        db_status = 'unknown'
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
                cursor.fetchone()
            db_status = 'ok'
        except Exception as e:
            db_status = f'error: {str(e)}'

        version = getattr(settings, 'APP_VERSION', None) or get_django_version()

        data = {
            'status': 'ok',
            'message': 'pong',
            'uptime_seconds': uptime_seconds,
            'db': db_status,
            'version': version,
            'timestamp': now.isoformat(),
            'api_root': request.build_absolute_uri('/api/'),
        }

        # If Accept: text/html, returns the pretty tile
        return Response(data, template_name=self.template_name)
