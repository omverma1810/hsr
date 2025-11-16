"""
Views for Testimonial Management (Phase 5).
Handles testimonial CRUD operations with ratings and verification.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone

from .models import Testimonial, Project
from .testimonial_serializers import (
    TestimonialListSerializer,
    TestimonialDetailSerializer,
    TestimonialCreateUpdateSerializer,
    BulkTestimonialActionSerializer,
)
from .utils import success_response, error_response
from .permissions import IsAdminUser


class TestimonialsListView(APIView):
    """
    GET: List all testimonials with filtering, search, sorting, pagination
    POST: Create new testimonial (admin only)
    """

    def get_permissions(self):
        """Allow authenticated users for GET, admin only for POST."""
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def get(self, request):
        """Get all testimonials with filtering and pagination."""
        try:
            # Query parameters
            project_id = request.query_params.get('project')
            is_active = request.query_params.get('is_active')
            verified = request.query_params.get('verified')
            min_rating = request.query_params.get('min_rating')
            search = request.query_params.get('search')
            sort_by = request.query_params.get('sort_by', '-created_at')
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 25))

            # Start with all non-deleted testimonials
            queryset = Testimonial.objects.select_related('project').all()

            # Apply filters
            if project_id:
                queryset = queryset.filter(project_id=project_id)

            if is_active is not None:
                queryset = queryset.filter(is_active=is_active.lower() == 'true')

            if verified is not None:
                queryset = queryset.filter(verified=verified.lower() == 'true')

            if min_rating:
                queryset = queryset.filter(rating__gte=int(min_rating))

            # Search
            if search:
                queryset = queryset.filter(
                    Q(customer_name__icontains=search) |
                    Q(quote__icontains=search) |
                    Q(project__title__icontains=search)
                )

            # Sorting
            allowed_sort_fields = [
                'created_at', '-created_at',
                'rating', '-rating',
                'display_order', '-display_order',
                'customer_name', '-customer_name',
            ]
            if sort_by in allowed_sort_fields:
                queryset = queryset.order_by(sort_by)

            # Count before pagination
            total = queryset.count()

            # Pagination
            start = (page - 1) * page_size
            end = start + page_size
            testimonials = queryset[start:end]

            # Serialize
            serializer = TestimonialListSerializer(testimonials, many=True)

            return success_response(
                data={
                    'testimonials': serializer.data,
                    'pagination': {
                        'total': total,
                        'page': page,
                        'page_size': page_size,
                        'total_pages': (total + page_size - 1) // page_size,
                    }
                },
                message='Testimonials retrieved successfully'
            )

        except Exception as e:
            return error_response(
                message='Failed to retrieve testimonials',
                errors={'error': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        """Create new testimonial (admin only)."""
        try:
            serializer = TestimonialCreateUpdateSerializer(data=request.data)

            if serializer.is_valid():
                testimonial = serializer.save()

                # Return detailed response
                detail_serializer = TestimonialDetailSerializer(testimonial)
                return success_response(
                    data=detail_serializer.data,
                    message='Testimonial created successfully',
                    status_code=status.HTTP_201_CREATED
                )

            return error_response(
                message='Validation failed',
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return error_response(
                message='Failed to create testimonial',
                errors={'error': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TestimonialDetailView(APIView):
    """
    GET: Get single testimonial details
    PUT: Update testimonial (admin only)
    DELETE: Delete testimonial (admin only, soft delete)
    """

    def get_permissions(self):
        """Allow authenticated users for GET, admin only for PUT/DELETE."""
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def get(self, request, pk):
        """Get testimonial details."""
        try:
            testimonial = Testimonial.objects.select_related('project').get(pk=pk)
            serializer = TestimonialDetailSerializer(testimonial)

            return success_response(
                data=serializer.data,
                message='Testimonial retrieved successfully'
            )

        except Testimonial.DoesNotExist:
            return error_response(
                message='Testimonial not found',
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                message='Failed to retrieve testimonial',
                errors={'error': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, pk):
        """Update testimonial (admin only)."""
        try:
            testimonial = Testimonial.objects.get(pk=pk)
            serializer = TestimonialCreateUpdateSerializer(
                testimonial,
                data=request.data,
                partial=True
            )

            if serializer.is_valid():
                serializer.save()

                # Return detailed response
                detail_serializer = TestimonialDetailSerializer(testimonial)
                return success_response(
                    data=detail_serializer.data,
                    message='Testimonial updated successfully'
                )

            return error_response(
                message='Validation failed',
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        except Testimonial.DoesNotExist:
            return error_response(
                message='Testimonial not found',
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                message='Failed to update testimonial',
                errors={'error': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, pk):
        """Soft delete testimonial (admin only)."""
        try:
            testimonial = Testimonial.objects.get(pk=pk)
            testimonial.soft_delete()

            return success_response(
                data={'id': pk},
                message='Testimonial deleted successfully'
            )

        except Testimonial.DoesNotExist:
            return error_response(
                message='Testimonial not found',
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                message='Failed to delete testimonial',
                errors={'error': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TestimonialRestoreView(APIView):
    """POST: Restore soft-deleted testimonial (admin only)."""

    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        """Restore soft-deleted testimonial."""
        try:
            testimonial = Testimonial.all_objects.get(pk=pk)

            if not testimonial.is_deleted:
                return error_response(
                    message='Testimonial is not deleted',
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            testimonial.restore()

            # Return detailed response
            detail_serializer = TestimonialDetailSerializer(testimonial)
            return success_response(
                data=detail_serializer.data,
                message='Testimonial restored successfully'
            )

        except Testimonial.DoesNotExist:
            return error_response(
                message='Testimonial not found',
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                message='Failed to restore testimonial',
                errors={'error': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BulkTestimonialActionsView(APIView):
    """POST: Perform bulk actions on testimonials (admin only)."""

    permission_classes = [IsAdminUser]

    def post(self, request):
        """Perform bulk actions on multiple testimonials."""
        try:
            serializer = BulkTestimonialActionSerializer(data=request.data)

            if not serializer.is_valid():
                return error_response(
                    message='Validation failed',
                    errors=serializer.errors,
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            testimonial_ids = serializer.validated_data['testimonial_ids']
            action = serializer.validated_data['action']

            # Get testimonials
            if action in ['delete', 'activate', 'deactivate', 'verify', 'unverify']:
                testimonials = Testimonial.objects.filter(id__in=testimonial_ids)
            else:  # restore
                testimonials = Testimonial.all_objects.filter(id__in=testimonial_ids)

            if not testimonials.exists():
                return error_response(
                    message='No testimonials found with provided IDs',
                    status_code=status.HTTP_404_NOT_FOUND
                )

            # Perform action
            updated_count = 0

            if action == 'delete':
                for testimonial in testimonials:
                    testimonial.soft_delete()
                    updated_count += 1

            elif action == 'restore':
                for testimonial in testimonials:
                    if testimonial.is_deleted:
                        testimonial.restore()
                        updated_count += 1

            elif action == 'activate':
                updated_count = testimonials.update(is_active=True)

            elif action == 'deactivate':
                updated_count = testimonials.update(is_active=False)

            elif action == 'verify':
                updated_count = testimonials.update(verified=True)

            elif action == 'unverify':
                updated_count = testimonials.update(verified=False)

            return success_response(
                data={
                    'action': action,
                    'updated_count': updated_count,
                    'testimonial_ids': testimonial_ids,
                },
                message=f'Bulk action "{action}" completed successfully on {updated_count} testimonials'
            )

        except Exception as e:
            return error_response(
                message='Failed to perform bulk action',
                errors={'error': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
