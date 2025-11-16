from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from django.utils import timezone
from django.conf import settings
from django.db import connection
from django import get_version as get_django_version
from .serializers import LoginSerializer, AdminUserSerializer, ChangePasswordSerializer
from .utils import success_response, error_response


class LoginView(APIView):
    """API endpoint for admin user login."""
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(description='Login successful'),
            400: OpenApiResponse(description='Invalid credentials'),
        },
        description='Authenticate admin user and return JWT tokens'
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']
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
            200: OpenApiResponse(description='Logout successful'),
            400: OpenApiResponse(description='Invalid token'),
        },
        description='Blacklist refresh token to logout user'
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
            200: AdminUserSerializer,
        },
        description='Get current authenticated admin user details'
    )
    def get(self, request):
        serializer = AdminUserSerializer(request.user)
        return success_response(
            data=serializer.data,
            message='User details retrieved successfully',
            status_code=status.HTTP_200_OK
        )


class ChangePasswordView(APIView):
    """API endpoint to change user password."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ChangePasswordSerializer,
        responses={
            200: OpenApiResponse(description='Password changed successfully'),
            400: OpenApiResponse(description='Validation errors'),
        },
        description='Change authenticated user password'
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
        responses={200: OpenApiResponse(description='Pong response')},
        description='Simple ping endpoint to check API liveness'
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
        }

        # If Accept: text/html, returns the pretty tile
        return Response(data, template_name=self.template_name)
