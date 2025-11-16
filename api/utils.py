from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import re


def custom_exception_handler(exc, context):
    """Custom exception handler for consistent API responses."""
    response = exception_handler(exc, context)

    if response is not None:
        custom_response = {
            'success': False,
            'message': 'An error occurred',
            'data': None,
            'errors': response.data
        }
        response.data = custom_response

    return response


def success_response(data=None, message='Success', status_code=status.HTTP_200_OK):
    """Standard success response format."""
    return Response({
        'success': True,
        'message': message,
        'data': data,
        'errors': None
    }, status=status_code)


def error_response(errors=None, message='Error', status_code=status.HTTP_400_BAD_REQUEST):
    """Standard error response format."""
    return Response({
        'success': False,
        'message': message,
        'data': None,
        'errors': errors
    }, status=status_code)


def validate_password(password):
    """
    Validate password complexity.
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character
    """
    errors = []

    if len(password) < 8:
        errors.append('Password must be at least 8 characters long')

    if not re.search(r'[A-Z]', password):
        errors.append('Password must contain at least one uppercase letter')

    if not re.search(r'[a-z]', password):
        errors.append('Password must contain at least one lowercase letter')

    if not re.search(r'\d', password):
        errors.append('Password must contain at least one number')

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append('Password must contain at least one special character')

    return errors
