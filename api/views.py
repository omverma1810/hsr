from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from drf_spectacular.utils import extend_schema, OpenApiResponse
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
