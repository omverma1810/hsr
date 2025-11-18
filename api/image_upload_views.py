from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.core.paginator import Paginator, EmptyPage

from .models import UploadedImage
from .image_upload_serializers import ImageUploadSerializer, UploadedImageSerializer
from .utils import success_response, error_response
from .permissions import IsAdminUser


class ImageUploadView(APIView):
    """
    Upload an image file.
    POST: Upload a new image (admin only)
    """
    
    permission_classes = [IsAuthenticated, IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]
    
    @extend_schema(
        request=ImageUploadSerializer,
        responses={
            201: OpenApiResponse(
                response=UploadedImageSerializer,
                description='Image uploaded successfully'
            ),
            400: OpenApiResponse(description='Invalid request data'),
            401: OpenApiResponse(description='Unauthorized'),
            403: OpenApiResponse(description='Forbidden - Admin access required'),
        },
        summary='Upload Image',
        description='Upload an image file. The image will be stored in /media/uploads/ and a public URL will be generated.'
    )
    def post(self, request):
        """Upload a new image."""
        try:
            serializer = ImageUploadSerializer(data=request.data, context={'request': request})
            
            if serializer.is_valid():
                uploaded_image = serializer.save()
                
                # Serialize the response
                response_serializer = UploadedImageSerializer(uploaded_image, context={'request': request})
                
                # Ensure image_url is set
                if not uploaded_image.image_url:
                    uploaded_image.image_url = uploaded_image.get_image_url(request=request)
                    uploaded_image.save(update_fields=['image_url'])
                
                return success_response(
                    data={
                        'success': True,
                        'imageUrl': uploaded_image.image_url,
                        'image': response_serializer.data
                    },
                    message='Image uploaded successfully',
                    status_code=status.HTTP_201_CREATED
                )
            else:
                return error_response(
                    message='Invalid image data',
                    errors=serializer.errors,
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            import traceback
            error_msg = str(e)
            error_trace = traceback.format_exc()
            
            # Check if it's a database table/column error
            if 'does not exist' in error_msg.lower() and ('relation' in error_msg.lower() or 'table' in error_msg.lower()):
                return error_response(
                    message='Database table not found. Please run migrations: python manage.py migrate',
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            # For other errors, return the actual error message for debugging
            return error_response(
                message=f'Error uploading image: {error_msg}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UploadedImagesListView(APIView):
    """
    List all uploaded images.
    GET: List all uploaded images (admin only)
    """
    
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    @extend_schema(
        parameters=[],
        responses={
            200: OpenApiResponse(
                response=UploadedImageSerializer(many=True),
                description='List of uploaded images'
            ),
            401: OpenApiResponse(description='Unauthorized'),
            403: OpenApiResponse(description='Forbidden - Admin access required'),
        },
        summary='List Uploaded Images',
        description='Get a list of all uploaded images'
    )
    def get(self, request):
        """List all uploaded images."""
        try:
            images = UploadedImage.objects.all().order_by('-created_at')
            
            # Pagination
            page_number = request.query_params.get('page', 1)
            page_size = request.query_params.get('page_size', 20)
            
            try:
                page_size = int(page_size)
                if page_size not in [10, 20, 50, 100]:
                    page_size = 20
            except (ValueError, TypeError):
                page_size = 20
            
            paginator = Paginator(images, page_size)
            
            try:
                page = paginator.page(page_number)
            except EmptyPage:
                page = paginator.page(1)
            
            serializer = UploadedImageSerializer(page.object_list, many=True, context={'request': request})
            
            return success_response(
                data={
                    'results': serializer.data,
                    'pagination': {
                        'page': page.number,
                        'page_size': page_size,
                        'total_pages': paginator.num_pages,
                        'total_count': paginator.count,
                        'has_next': page.has_next(),
                        'has_previous': page.has_previous(),
                    }
                },
                message='Images retrieved successfully'
            )
        except Exception as e:
            import traceback
            error_msg = str(e)
            error_trace = traceback.format_exc()
            
            # Check if it's a database table/column error
            if 'does not exist' in error_msg.lower() and ('relation' in error_msg.lower() or 'table' in error_msg.lower()):
                return error_response(
                    message='Database table not found. Please run migrations: python manage.py migrate',
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            # For other errors, return the actual error message for debugging
            return error_response(
                message=f'Error retrieving images: {error_msg}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UploadedImageDetailView(APIView):
    """
    Retrieve or delete a specific uploaded image.
    GET: Get image details (admin only)
    DELETE: Delete an image (admin only)
    """
    
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    @extend_schema(
        responses={
            200: OpenApiResponse(
                response=UploadedImageSerializer,
                description='Image details'
            ),
            404: OpenApiResponse(description='Image not found'),
        },
        summary='Get Image Details',
        description='Get details of a specific uploaded image'
    )
    def get(self, request, pk):
        """Get image details."""
        try:
            image = UploadedImage.objects.get(pk=pk)
            serializer = UploadedImageSerializer(image, context={'request': request})
            return success_response(
                data=serializer.data,
                message='Image retrieved successfully'
            )
        except UploadedImage.DoesNotExist:
            return error_response(
                message='Image not found',
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                message=f'Error retrieving image: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        responses={
            200: OpenApiResponse(description='Image deleted successfully'),
            404: OpenApiResponse(description='Image not found'),
        },
        summary='Delete Image',
        description='Delete an uploaded image'
    )
    def delete(self, request, pk):
        """Delete an image."""
        try:
            image = UploadedImage.objects.get(pk=pk)
            image.delete()
            return success_response(
                message='Image deleted successfully'
            )
        except UploadedImage.DoesNotExist:
            return error_response(
                message='Image not found',
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                message=f'Error deleting image: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

