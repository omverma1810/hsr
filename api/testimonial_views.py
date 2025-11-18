from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.db.models import Q
from .models import Testimonial
from .testimonial_serializers import TestimonialSerializer, TestimonialListSerializer
from .permissions import IsAdminUser
from .utils import success_response, error_response
from rest_framework import status


class TestimonialsListView(APIView):
    """List and create testimonials."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(
        responses={200: TestimonialListSerializer(many=True)},
        description="List all testimonials (admin only, with filtering and pagination)"
    )
    def get(self, request):
        try:
            # Query parameters
            is_active = request.query_params.get('is_active')
            project_id = request.query_params.get('project_id')
            search = request.query_params.get('search', '')
            include_deleted = request.query_params.get('include_deleted', 'false').lower() == 'true'
            
            # Build query
            queryset = Testimonial.objects.select_related('project').all()
            
            if not include_deleted:
                queryset = queryset.filter(is_deleted=False)
            
            if is_active is not None:
                queryset = queryset.filter(is_active=is_active.lower() == 'true')
            
            if project_id:
                queryset = queryset.filter(project_id=project_id)
            
            if search:
                queryset = queryset.filter(
                    Q(customer_name__icontains=search) |
                    Q(quote__icontains=search) |
                    Q(project__title__icontains=search)
                )
            
            # Order by display_order, then created_at
            queryset = queryset.order_by('display_order', '-created_at')
            
            serializer = TestimonialListSerializer(queryset, many=True)
            return success_response(
                data=serializer.data,
                message="Testimonials retrieved successfully"
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to retrieve testimonials"
            )

    @extend_schema(
        request=TestimonialSerializer,
        responses={201: TestimonialSerializer},
        description="Create a new testimonial (admin only)"
    )
    def post(self, request):
        try:
            serializer = TestimonialSerializer(data=request.data)
            if serializer.is_valid():
                testimonial = serializer.save()
                response_serializer = TestimonialSerializer(testimonial)
                return success_response(
                    data=response_serializer.data,
                    message="Testimonial created successfully",
                    status_code=status.HTTP_201_CREATED
                )
            return error_response(
                errors=serializer.errors,
                message="Failed to create testimonial"
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to create testimonial"
            )


class TestimonialDetailView(APIView):
    """Retrieve, update, or delete a testimonial."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_object(self, pk):
        try:
            return Testimonial.objects.select_related('project').get(pk=pk, is_deleted=False)
        except Testimonial.DoesNotExist:
            return None

    @extend_schema(
        responses={200: TestimonialSerializer},
        description="Get testimonial details (admin only)"
    )
    def get(self, request, pk):
        testimonial = self.get_object(pk)
        if not testimonial:
            return error_response(
                errors={'detail': 'Testimonial not found'},
                message="Testimonial not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        serializer = TestimonialSerializer(testimonial)
        return success_response(
            data=serializer.data,
            message="Testimonial retrieved successfully"
        )

    @extend_schema(
        request=TestimonialSerializer,
        responses={200: TestimonialSerializer},
        description="Update testimonial (admin only)"
    )
    def put(self, request, pk):
        testimonial = self.get_object(pk)
        if not testimonial:
            return error_response(
                errors={'detail': 'Testimonial not found'},
                message="Testimonial not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        serializer = TestimonialSerializer(testimonial, data=request.data, partial=True)
        if serializer.is_valid():
            testimonial = serializer.save()
            response_serializer = TestimonialSerializer(testimonial)
            return success_response(
                data=response_serializer.data,
                message="Testimonial updated successfully"
            )
        return error_response(
            errors=serializer.errors,
            message="Failed to update testimonial"
        )

    patch = put  # Support both PUT and PATCH

    @extend_schema(
        responses={200: OpenApiResponse(description="Testimonial deleted successfully")},
        description="Delete testimonial (admin only, soft delete)"
    )
    def delete(self, request, pk):
        testimonial = self.get_object(pk)
        if not testimonial:
            return error_response(
                errors={'detail': 'Testimonial not found'},
                message="Testimonial not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        try:
            testimonial.soft_delete()
            return success_response(
                message="Testimonial deleted successfully"
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to delete testimonial"
            )


class TestimonialRestoreView(APIView):
    """Restore a soft-deleted testimonial."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(
        responses={
            200: OpenApiResponse(description='Testimonial restored successfully - Returns the restored testimonial details.'),
            404: OpenApiResponse(description='Not found - Deleted testimonial does not exist.'),
        },
        description='''
        **Restore Testimonial**
        
        Restore a soft-deleted testimonial. This will set `is_deleted=False` and make the testimonial visible again.
        
        **Use Cases:**
        - Recover accidentally deleted testimonials
        - Restore testimonials from trash
        
        **Note:** Only soft-deleted testimonials can be restored. If a testimonial was never deleted, you'll get a 404 error.
        
        **Authentication Required:** Yes (Admin only)
        ''',
        tags=['Testimonials']
    )
    def post(self, request, pk):
        try:
            testimonial = Testimonial.objects.get(pk=pk, is_deleted=True)
            testimonial.restore()
            serializer = TestimonialSerializer(testimonial)
            return success_response(
                data=serializer.data,
                message="Testimonial restored successfully"
            )
        except Testimonial.DoesNotExist:
            return error_response(
                errors={'detail': 'Deleted testimonial not found'},
                message="Testimonial not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to restore testimonial"
            )

