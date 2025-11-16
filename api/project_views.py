from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.db.models import Q, Count, Prefetch
from django.core.paginator import Paginator, EmptyPage
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
import csv
from django.http import HttpResponse

from .models import Project, ProjectGalleryImage, ProjectFloorPlan, PROJECT_CONFIGURATIONS, PROJECT_AMENITIES
from .project_serializers import (
    ProjectListSerializer,
    ProjectDetailSerializer,
    ProjectCreateUpdateSerializer,
    ProjectGalleryImageSerializer,
    ProjectFloorPlanSerializer,
    AddGalleryImageSerializer,
    AddFloorPlanSerializer,
    ProjectConfigurationsSerializer,
    ProjectAmenitiesSerializer,
    BulkActionSerializer
)
from .utils import success_response, error_response
from .permissions import IsAdminUser


class ProjectsListView(APIView):
    """
    List all projects with filtering, searching, sorting, and pagination.
    GET: Public access (shows only non-deleted projects)
    POST: Admin only (create new project)
    """

    def get_permissions(self):
        """Public GET, admin POST."""
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]

    @extend_schema(
        parameters=[
            OpenApiParameter('status', str, description='Filter by status (upcoming/ongoing/completed)'),
            OpenApiParameter('is_featured', bool, description='Filter by featured status'),
            OpenApiParameter('search', str, description='Search in title, location, RERA number'),
            OpenApiParameter('sort_by', str, description='Sort by field (created_at, updated_at, title, status)'),
            OpenApiParameter('sort_order', str, description='Sort order (asc/desc)'),
            OpenApiParameter('page', int, description='Page number'),
            OpenApiParameter('page_size', int, description='Items per page (10/25/50/100)'),
            OpenApiParameter('include_deleted', bool, description='Include deleted projects (admin only)'),
        ],
        responses={200: ProjectListSerializer(many=True)},
        description="List all projects with advanced filtering and pagination"
    )
    def get(self, request):
        """List projects with filtering."""
        try:
            # Base queryset
            if request.user.is_authenticated and request.user.is_staff:
                # Admin can see deleted projects if requested
                include_deleted = request.query_params.get('include_deleted', 'false').lower() == 'true'
                if include_deleted:
                    queryset = Project.all_objects.all()
                else:
                    queryset = Project.objects.all()
            else:
                # Public only sees non-deleted projects
                queryset = Project.objects.all()

            # Optimize queries
            queryset = queryset.select_related('created_by')

            # Filtering
            status_filter = request.query_params.get('status')
            if status_filter:
                queryset = queryset.filter(status=status_filter)

            is_featured = request.query_params.get('is_featured')
            if is_featured is not None:
                is_featured_bool = is_featured.lower() == 'true'
                queryset = queryset.filter(is_featured=is_featured_bool)

            # Searching
            search = request.query_params.get('search')
            if search:
                queryset = queryset.filter(
                    Q(title__icontains=search) |
                    Q(location__icontains=search) |
                    Q(rera_number__icontains=search) |
                    Q(description__icontains=search)
                )

            # Sorting
            sort_by = request.query_params.get('sort_by', 'created_at')
            sort_order = request.query_params.get('sort_order', 'desc')

            valid_sort_fields = ['created_at', 'updated_at', 'title', 'status', 'view_count']
            if sort_by not in valid_sort_fields:
                sort_by = 'created_at'

            if sort_order == 'asc':
                queryset = queryset.order_by(sort_by)
            else:
                queryset = queryset.order_by(f'-{sort_by}')

            # Pagination
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))

            # Limit page_size
            valid_page_sizes = [10, 25, 50, 100]
            if page_size not in valid_page_sizes:
                page_size = 10

            paginator = Paginator(queryset, page_size)

            try:
                projects = paginator.page(page)
            except EmptyPage:
                projects = paginator.page(paginator.num_pages)

            serializer = ProjectListSerializer(projects, many=True)

            return success_response(
                data={
                    'results': serializer.data,
                    'pagination': {
                        'current_page': projects.number,
                        'total_pages': paginator.num_pages,
                        'total_items': paginator.count,
                        'page_size': page_size,
                        'has_next': projects.has_next(),
                        'has_previous': projects.has_previous(),
                    }
                },
                message=f"Retrieved {len(serializer.data)} projects"
            )

        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to retrieve projects"
            )

    @extend_schema(
        request=ProjectCreateUpdateSerializer,
        responses={201: ProjectDetailSerializer},
        description="Create new project (admin only)"
    )
    def post(self, request):
        """Create new project."""
        try:
            serializer = ProjectCreateUpdateSerializer(
                data=request.data,
                context={'request': request}
            )

            if serializer.is_valid():
                project = serializer.save()
                response_serializer = ProjectDetailSerializer(project)

                return success_response(
                    data=response_serializer.data,
                    message=f"Project '{project.title}' created successfully",
                    status_code=status.HTTP_201_CREATED
                )

            return error_response(
                errors=serializer.errors,
                message="Failed to create project"
            )

        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to create project"
            )


class ProjectDetailView(APIView):
    """
    Get, update, or delete a specific project.
    GET: Public access (increments view count)
    PUT/PATCH: Admin only
    DELETE: Admin only (soft delete)
    """

    def get_permissions(self):
        """Public GET, admin PUT/DELETE."""
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]

    def get_object(self, pk, include_deleted=False):
        """Get project by ID."""
        try:
            if include_deleted:
                return Project.all_objects.select_related(
                    'created_by', 'updated_by'
                ).prefetch_related(
                    'gallery_images',
                    'floor_plans'
                ).get(pk=pk)
            else:
                return Project.objects.select_related(
                    'created_by', 'updated_by'
                ).prefetch_related(
                    'gallery_images',
                    'floor_plans'
                ).get(pk=pk)
        except Project.DoesNotExist:
            return None

    @extend_schema(
        responses={200: ProjectDetailSerializer},
        description="Get project details (public access, increments view count)"
    )
    def get(self, request, pk):
        """Get project details."""
        try:
            project = self.get_object(pk)

            if not project:
                return error_response(
                    errors={'detail': 'Project not found'},
                    message="Project not found",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            # Increment view count (only for public access)
            if not (request.user.is_authenticated and request.user.is_staff):
                project.increment_view_count()

            serializer = ProjectDetailSerializer(project)

            return success_response(
                data=serializer.data,
                message="Project retrieved successfully"
            )

        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to retrieve project"
            )

    @extend_schema(
        request=ProjectCreateUpdateSerializer,
        responses={200: ProjectDetailSerializer},
        description="Update project (admin only, partial updates supported)"
    )
    def put(self, request, pk):
        """Update project (full or partial)."""
        try:
            project = self.get_object(pk, include_deleted=True)

            if not project:
                return error_response(
                    errors={'detail': 'Project not found'},
                    message="Project not found",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            serializer = ProjectCreateUpdateSerializer(
                project,
                data=request.data,
                partial=True,
                context={'request': request}
            )

            if serializer.is_valid():
                project = serializer.save()
                response_serializer = ProjectDetailSerializer(project)

                return success_response(
                    data=response_serializer.data,
                    message=f"Project '{project.title}' updated successfully"
                )

            return error_response(
                errors=serializer.errors,
                message="Failed to update project"
            )

        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to update project"
            )

    patch = put  # Support both PUT and PATCH

    @extend_schema(
        responses={200: OpenApiResponse(description="Project deleted (soft delete)")},
        description="Delete project (admin only, soft delete)"
    )
    def delete(self, request, pk):
        """Soft delete project."""
        try:
            project = self.get_object(pk)

            if not project:
                return error_response(
                    errors={'detail': 'Project not found'},
                    message="Project not found",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            # Check if project has leads
            if project.leads.filter(is_deleted=False).exists():
                return error_response(
                    errors={'detail': 'Cannot delete project with associated leads'},
                    message="This project has associated leads. Please handle them first.",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            # Soft delete
            project_title = project.title
            project.soft_delete()

            return success_response(
                message=f"Project '{project_title}' deleted successfully"
            )

        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to delete project"
            )


class ProjectGalleryView(APIView):
    """Manage project gallery images."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(
        responses={200: ProjectGalleryImageSerializer(many=True)},
        description="Get all gallery images for a project"
    )
    def get(self, request, pk):
        """Get project gallery images."""
        try:
            project = Project.objects.get(pk=pk)
            images = project.gallery_images.filter(is_deleted=False).order_by('display_order', 'created_at')
            serializer = ProjectGalleryImageSerializer(images, many=True)

            return success_response(
                data=serializer.data,
                message=f"Retrieved {images.count()} gallery images"
            )
        except Project.DoesNotExist:
            return error_response(
                errors={'detail': 'Project not found'},
                message="Project not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        request=AddGalleryImageSerializer,
        responses={201: ProjectGalleryImageSerializer},
        description="Add gallery image to project"
    )
    def post(self, request, pk):
        """Add gallery image."""
        try:
            project = Project.objects.get(pk=pk)
            serializer = AddGalleryImageSerializer(data=request.data)

            if serializer.is_valid():
                image = ProjectGalleryImage.objects.create(
                    project=project,
                    **serializer.validated_data
                )

                response_serializer = ProjectGalleryImageSerializer(image)

                return success_response(
                    data=response_serializer.data,
                    message="Gallery image added successfully",
                    status_code=status.HTTP_201_CREATED
                )

            return error_response(
                errors=serializer.errors,
                message="Failed to add gallery image"
            )
        except Project.DoesNotExist:
            return error_response(
                errors={'detail': 'Project not found'},
                message="Project not found",
                status_code=status.HTTP_404_NOT_FOUND
            )


class ProjectGalleryImageDetailView(APIView):
    """Update or delete a specific gallery image."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(
        request=ProjectGalleryImageSerializer,
        responses={200: ProjectGalleryImageSerializer},
        description="Update gallery image"
    )
    def put(self, request, pk, image_id):
        """Update gallery image."""
        try:
            image = ProjectGalleryImage.objects.get(pk=image_id, project_id=pk)
            serializer = ProjectGalleryImageSerializer(image, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return success_response(
                    data=serializer.data,
                    message="Gallery image updated successfully"
                )

            return error_response(
                errors=serializer.errors,
                message="Failed to update gallery image"
            )
        except ProjectGalleryImage.DoesNotExist:
            return error_response(
                errors={'detail': 'Gallery image not found'},
                message="Gallery image not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        responses={200: OpenApiResponse(description="Gallery image deleted")},
        description="Delete gallery image"
    )
    def delete(self, request, pk, image_id):
        """Delete gallery image."""
        try:
            image = ProjectGalleryImage.objects.get(pk=image_id, project_id=pk)
            image.soft_delete()

            return success_response(
                message="Gallery image deleted successfully"
            )
        except ProjectGalleryImage.DoesNotExist:
            return error_response(
                errors={'detail': 'Gallery image not found'},
                message="Gallery image not found",
                status_code=status.HTTP_404_NOT_FOUND
            )


class ProjectFloorPlansView(APIView):
    """Manage project floor plans."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(
        responses={200: ProjectFloorPlanSerializer(many=True)},
        description="Get all floor plans for a project"
    )
    def get(self, request, pk):
        """Get project floor plans."""
        try:
            project = Project.objects.get(pk=pk)
            floor_plans = project.floor_plans.filter(is_deleted=False).order_by('display_order', 'created_at')
            serializer = ProjectFloorPlanSerializer(floor_plans, many=True)

            return success_response(
                data=serializer.data,
                message=f"Retrieved {floor_plans.count()} floor plans"
            )
        except Project.DoesNotExist:
            return error_response(
                errors={'detail': 'Project not found'},
                message="Project not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        request=AddFloorPlanSerializer,
        responses={201: ProjectFloorPlanSerializer},
        description="Add floor plan to project"
    )
    def post(self, request, pk):
        """Add floor plan."""
        try:
            project = Project.objects.get(pk=pk)
            serializer = AddFloorPlanSerializer(data=request.data)

            if serializer.is_valid():
                floor_plan = ProjectFloorPlan.objects.create(
                    project=project,
                    **serializer.validated_data
                )

                response_serializer = ProjectFloorPlanSerializer(floor_plan)

                return success_response(
                    data=response_serializer.data,
                    message="Floor plan added successfully",
                    status_code=status.HTTP_201_CREATED
                )

            return error_response(
                errors=serializer.errors,
                message="Failed to add floor plan"
            )
        except Project.DoesNotExist:
            return error_response(
                errors={'detail': 'Project not found'},
                message="Project not found",
                status_code=status.HTTP_404_NOT_FOUND
            )


class ProjectFloorPlanDetailView(APIView):
    """Update or delete a specific floor plan."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(
        request=ProjectFloorPlanSerializer,
        responses={200: ProjectFloorPlanSerializer},
        description="Update floor plan"
    )
    def put(self, request, pk, plan_id):
        """Update floor plan."""
        try:
            floor_plan = ProjectFloorPlan.objects.get(pk=plan_id, project_id=pk)
            serializer = ProjectFloorPlanSerializer(floor_plan, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return success_response(
                    data=serializer.data,
                    message="Floor plan updated successfully"
                )

            return error_response(
                errors=serializer.errors,
                message="Failed to update floor plan"
            )
        except ProjectFloorPlan.DoesNotExist:
            return error_response(
                errors={'detail': 'Floor plan not found'},
                message="Floor plan not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        responses={200: OpenApiResponse(description="Floor plan deleted")},
        description="Delete floor plan"
    )
    def delete(self, request, pk, plan_id):
        """Delete floor plan."""
        try:
            floor_plan = ProjectFloorPlan.objects.get(pk=plan_id, project_id=pk)
            floor_plan.soft_delete()

            return success_response(
                message="Floor plan deleted successfully"
            )
        except ProjectFloorPlan.DoesNotExist:
            return error_response(
                errors={'detail': 'Floor plan not found'},
                message="Floor plan not found",
                status_code=status.HTTP_404_NOT_FOUND
            )


class ProjectRestoreView(APIView):
    """Restore a soft-deleted project."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(
        responses={200: ProjectDetailSerializer},
        description="Restore a soft-deleted project"
    )
    def post(self, request, pk):
        """Restore deleted project."""
        try:
            project = Project.all_objects.get(pk=pk)

            if not project.is_deleted:
                return error_response(
                    errors={'detail': 'Project is not deleted'},
                    message="Project is not deleted",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            project.restore()
            serializer = ProjectDetailSerializer(project)

            return success_response(
                data=serializer.data,
                message=f"Project '{project.title}' restored successfully"
            )
        except Project.DoesNotExist:
            return error_response(
                errors={'detail': 'Project not found'},
                message="Project not found",
                status_code=status.HTTP_404_NOT_FOUND
            )


class ProjectCloneView(APIView):
    """Clone/duplicate a project."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(
        responses={201: ProjectDetailSerializer},
        description="Clone an existing project"
    )
    def post(self, request, pk):
        """Clone project."""
        try:
            original = Project.objects.get(pk=pk)

            # Create new project with cloned data
            cloned = Project.objects.create(
                title=f"{original.title} (Copy)",
                location=original.location,
                rera_number=f"{original.rera_number}-COPY",  # Must be unique
                description=original.description,
                status=original.status,
                hero_image_url=original.hero_image_url,
                configurations=original.configurations,
                amenities=original.amenities,
                is_featured=False,  # Don't clone featured status
                created_by=request.user,
                updated_by=request.user
            )

            # Clone gallery images
            for image in original.gallery_images.filter(is_deleted=False):
                ProjectGalleryImage.objects.create(
                    project=cloned,
                    image_url=image.image_url,
                    caption=image.caption,
                    display_order=image.display_order
                )

            # Clone floor plans
            for plan in original.floor_plans.filter(is_deleted=False):
                ProjectFloorPlan.objects.create(
                    project=cloned,
                    title=plan.title,
                    file_url=plan.file_url,
                    display_order=plan.display_order
                )

            serializer = ProjectDetailSerializer(cloned)

            return success_response(
                data=serializer.data,
                message=f"Project cloned successfully. Update RERA number to make it unique.",
                status_code=status.HTTP_201_CREATED
            )
        except Project.DoesNotExist:
            return error_response(
                errors={'detail': 'Project not found'},
                message="Project not found",
                status_code=status.HTTP_404_NOT_FOUND
            )


class BulkActionsView(APIView):
    """Perform bulk actions on multiple projects."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(
        request=BulkActionSerializer,
        responses={200: OpenApiResponse(description="Bulk action completed")},
        description="Perform bulk actions (delete, restore, feature, change_status)"
    )
    def post(self, request):
        """Perform bulk action."""
        try:
            serializer = BulkActionSerializer(data=request.data)

            if not serializer.is_valid():
                return error_response(
                    errors=serializer.errors,
                    message="Invalid bulk action data"
                )

            project_ids = serializer.validated_data['project_ids']
            action = serializer.validated_data['action']

            if action == 'delete':
                projects = Project.objects.filter(id__in=project_ids)
                count = projects.count()
                for project in projects:
                    project.soft_delete()
                message = f"{count} projects deleted successfully"

            elif action == 'restore':
                projects = Project.all_objects.filter(id__in=project_ids, is_deleted=True)
                count = projects.count()
                for project in projects:
                    project.restore()
                message = f"{count} projects restored successfully"

            elif action == 'feature':
                projects = Project.objects.filter(id__in=project_ids)
                count = projects.update(is_featured=True)
                message = f"{count} projects marked as featured"

            elif action == 'unfeature':
                projects = Project.objects.filter(id__in=project_ids)
                count = projects.update(is_featured=False)
                message = f"{count} projects unmarked as featured"

            elif action == 'change_status':
                new_status = serializer.validated_data['status']
                projects = Project.objects.filter(id__in=project_ids)
                count = projects.update(status=new_status, updated_by=request.user)
                message = f"{count} projects status changed to {new_status}"

            return success_response(message=message)

        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Bulk action failed"
            )


class ExportProjectsView(APIView):
    """Export projects to CSV."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        """Export projects to CSV."""
        try:
            projects = Project.objects.all().select_related('created_by')

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="projects_export.csv"'

            writer = csv.writer(response)
            writer.writerow([
                'ID', 'Title', 'Location', 'RERA Number', 'Status',
                'Is Featured', 'View Count', 'Created By', 'Created At'
            ])

            for project in projects:
                writer.writerow([
                    project.id,
                    project.title,
                    project.location,
                    project.rera_number,
                    project.status,
                    project.is_featured,
                    project.view_count,
                    project.created_by.full_name if project.created_by else '',
                    project.created_at.strftime('%Y-%m-%d %H:%M:%S')
                ])

            return response
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Export failed"
            )


class ConfigurationsListView(APIView):
    """Get list of available project configurations."""
    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: ProjectConfigurationsSerializer(many=True)},
        description="Get list of available project configurations"
    )
    def get(self, request):
        """Get configurations list."""
        data = [{'key': key, 'label': label} for key, label in PROJECT_CONFIGURATIONS]
        return success_response(
            data=data,
            message="Retrieved project configurations"
        )


class AmenitiesListView(APIView):
    """Get list of available project amenities."""
    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: ProjectAmenitiesSerializer(many=True)},
        description="Get list of available project amenities"
    )
    def get(self, request):
        """Get amenities list."""
        data = [{'key': key, 'label': label} for key, label in PROJECT_AMENITIES]
        return success_response(
            data=data,
            message="Retrieved project amenities"
        )
