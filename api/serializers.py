from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import AdminUser
from .utils import validate_password


class AdminUserSerializer(serializers.ModelSerializer):
    """Serializer for AdminUser model."""

    class Meta:
        model = AdminUser
        fields = ['id', 'email', 'full_name', 'role', 'is_active', 'is_staff', 'last_login', 'date_joined']
        read_only_fields = ['id', 'last_login', 'date_joined']


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            raise serializers.ValidationError('Email and password are required')

        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError('Invalid email or password')

        if not user.is_active:
            raise serializers.ValidationError('User account is disabled')

        data['user'] = user
        return data


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password."""
    current_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate_current_password(self, value):
        """Validate current password."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect')
        return value

    def validate(self, data):
        """Validate password matching and complexity."""
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match'})

        # Validate password complexity
        password_errors = validate_password(data['new_password'])
        if password_errors:
            raise serializers.ValidationError({'new_password': password_errors})

        return data

    def save(self):
        """Update user password."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class ResetPasswordSerializer(serializers.Serializer):
    """Serializer for resetting password (without current password)."""
    email = serializers.EmailField(required=True)
    new_password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate_email(self, value):
        """Validate that email exists and belongs to an admin user."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.get(email=value, is_staff=True)
        except User.DoesNotExist:
            raise serializers.ValidationError('No admin account found with this email address.')
        return value

    def validate(self, data):
        """Validate password matching and complexity."""
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match'})

        # Validate password complexity
        password_errors = validate_password(data['new_password'])
        if password_errors:
            raise serializers.ValidationError({'new_password': password_errors})

        return data

    def save(self):
        """Update user password."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(email=self.validated_data['email'], is_staff=True)
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
