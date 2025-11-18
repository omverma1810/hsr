from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import HomePageContent, FeaturedProject, Testimonial, PageHeroImages
from .homepage_serializers import (
    HomePageContentSerializer,
    HomePageContentUpdateSerializer,
    HeroSectionSerializer,
    StatisticsSectionSerializer,
    FooterInfoSerializer,
    FeaturedProjectSerializer,
    AddFeaturedProjectSerializer,
    TestimonialDisplaySerializer,
    CompleteHomePageSerializer,
    PageHeroImagesSerializer
)
from .utils import success_response, error_response
from .permissions import IsAdminUser


class HomePageContentView(APIView):
    """
    Get or update complete home page content.
    GET: Public access
    PUT: Admin only
    """

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]

    @extend_schema(
        responses={200: HomePageContentSerializer},
        description="Get complete home page content (public access)"
    )
    def get(self, request):
        try:
            content = HomePageContent.get_current()
            serializer = HomePageContentSerializer(content)
            return success_response(
                data=serializer.data,
                message="Home page content retrieved successfully"
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to retrieve home page content"
            )

    @extend_schema(
        request=HomePageContentUpdateSerializer,
        responses={200: HomePageContentSerializer},
        description="Update home page content (admin only)"
    )
    def put(self, request):
        try:
            content = HomePageContent.get_current()
            serializer = HomePageContentUpdateSerializer(content, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                response_serializer = HomePageContentSerializer(content)
                return success_response(
                    data=response_serializer.data,
                    message="Home page content updated successfully"
                )

            return error_response(
                errors=serializer.errors,
                message="Failed to update home page content"
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to update home page content"
            )


class HeroSectionView(APIView):
    """
    Get or update hero section only.
    GET: Public access
    PUT: Admin only
    """

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]

    @extend_schema(
        responses={200: HeroSectionSerializer},
        description="Get hero section content (public access)"
    )
    def get(self, request):
        try:
            content = HomePageContent.get_current()
            serializer = HeroSectionSerializer(content)
            return success_response(
                data=serializer.data,
                message="Hero section retrieved successfully"
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to retrieve hero section"
            )

    @extend_schema(
        request=HeroSectionSerializer,
        responses={200: HeroSectionSerializer},
        description="Update hero section (admin only)"
    )
    def put(self, request):
        try:
            content = HomePageContent.get_current()
            serializer = HeroSectionSerializer(content, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return success_response(
                    data=serializer.data,
                    message="Hero section updated successfully"
                )

            return error_response(
                errors=serializer.errors,
                message="Failed to update hero section"
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to update hero section"
            )


class StatisticsSectionView(APIView):
    """
    Get or update statistics section only.
    GET: Public access
    PUT: Admin only
    """

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]

    @extend_schema(
        responses={200: StatisticsSectionSerializer},
        description="Get statistics section (public access)"
    )
    def get(self, request):
        try:
            content = HomePageContent.get_current()
            serializer = StatisticsSectionSerializer(content)
            return success_response(
                data=serializer.data,
                message="Statistics section retrieved successfully"
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to retrieve statistics section"
            )

    @extend_schema(
        request=HomePageContentUpdateSerializer,
        responses={200: StatisticsSectionSerializer},
        description="Update statistics section (admin only)"
    )
    def put(self, request):
        try:
            content = HomePageContent.get_current()
            # Only update statistics fields
            stats_fields = {
                'stats_experience_value', 'stats_experience_label',
                'stats_projects_value', 'stats_projects_label',
                'stats_families_value', 'stats_families_label',
                'stats_sqft_value', 'stats_sqft_label'
            }
            stats_data = {k: v for k, v in request.data.items() if k in stats_fields}

            serializer = HomePageContentUpdateSerializer(content, data=stats_data, partial=True)

            if serializer.is_valid():
                serializer.save()
                response_serializer = StatisticsSectionSerializer(content)
                return success_response(
                    data=response_serializer.data,
                    message="Statistics section updated successfully"
                )

            return error_response(
                errors=serializer.errors,
                message="Failed to update statistics section"
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to update statistics section"
            )


class FooterInfoView(APIView):
    """
    Get or update footer information only.
    GET: Public access
    PUT: Admin only
    """

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]

    @extend_schema(
        responses={200: FooterInfoSerializer},
        description="Get footer information (public access)"
    )
    def get(self, request):
        try:
            content = HomePageContent.get_current()
            serializer = FooterInfoSerializer(content)
            return success_response(
                data=serializer.data,
                message="Footer information retrieved successfully"
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to retrieve footer information"
            )

    @extend_schema(
        request=FooterInfoSerializer,
        responses={200: FooterInfoSerializer},
        description="Update footer information (admin only)"
    )
    def put(self, request):
        try:
            content = HomePageContent.get_current()
            serializer = FooterInfoSerializer(content, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return success_response(
                    data=serializer.data,
                    message="Footer information updated successfully"
                )

            return error_response(
                errors=serializer.errors,
                message="Failed to update footer information"
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to update footer information"
            )


class FeaturedProjectsListView(APIView):
    """
    Get all featured projects or add a new featured project.
    GET: Public access
    POST: Admin only
    """

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]

    @extend_schema(
        responses={200: FeaturedProjectSerializer(many=True)},
        description="Get all featured projects (public access)"
    )
    def get(self, request):
        try:
            # Get active featured projects only for public
            # Admins can see all by passing ?all=true
            show_all = request.query_params.get('all') == 'true' and request.user.is_authenticated

            if show_all:
                featured_projects = FeaturedProject.objects.filter(
                    project__is_deleted=False
                ).select_related('project').order_by('display_order')
            else:
                featured_projects = FeaturedProject.objects.filter(
                    is_active=True,
                    project__is_deleted=False
                ).select_related('project').order_by('display_order')

            serializer = FeaturedProjectSerializer(featured_projects, many=True)
            return success_response(
                data=serializer.data,
                message=f"Retrieved {featured_projects.count()} featured projects"
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to retrieve featured projects"
            )

    @extend_schema(
        request=AddFeaturedProjectSerializer,
        responses={201: FeaturedProjectSerializer},
        description="Add a new featured project (admin only)"
    )
    def post(self, request):
        try:
            serializer = AddFeaturedProjectSerializer(data=request.data)

            if serializer.is_valid():
                featured_project = serializer.save()
                response_serializer = FeaturedProjectSerializer(featured_project)
                return success_response(
                    data=response_serializer.data,
                    message="Featured project added successfully",
                    status_code=201
                )

            return error_response(
                errors=serializer.errors,
                message="Failed to add featured project"
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to add featured project"
            )


class FeaturedProjectDetailView(APIView):
    """
    Get, update, or delete a specific featured project.
    GET: Public access
    PUT/DELETE: Admin only
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(
        responses={200: FeaturedProjectSerializer},
        description="Get specific featured project details (admin only)"
    )
    def get(self, request, pk):
        try:
            featured_project = FeaturedProject.objects.select_related('project').get(pk=pk)
            serializer = FeaturedProjectSerializer(featured_project)
            return success_response(
                data=serializer.data,
                message="Featured project retrieved successfully"
            )
        except FeaturedProject.DoesNotExist:
            return error_response(
                errors={'detail': 'Featured project not found'},
                message="Featured project not found",
                status_code=404
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to retrieve featured project"
            )

    @extend_schema(
        request=FeaturedProjectSerializer,
        responses={200: FeaturedProjectSerializer},
        description="Update featured project (admin only)"
    )
    def put(self, request, pk):
        try:
            featured_project = FeaturedProject.objects.get(pk=pk)
            serializer = FeaturedProjectSerializer(featured_project, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return success_response(
                    data=serializer.data,
                    message="Featured project updated successfully"
                )

            return error_response(
                errors=serializer.errors,
                message="Failed to update featured project"
            )
        except FeaturedProject.DoesNotExist:
            return error_response(
                errors={'detail': 'Featured project not found'},
                message="Featured project not found",
                status_code=404
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to update featured project"
            )

    @extend_schema(
        responses={200: OpenApiResponse(description="Featured project deleted successfully")},
        description="Delete featured project (admin only)"
    )
    def delete(self, request, pk):
        try:
            featured_project = FeaturedProject.objects.get(pk=pk)
            project_title = featured_project.project.title
            featured_project.delete()
            return success_response(
                data={'id': pk},
                message=f"Featured project '{project_title}' removed successfully"
            )
        except FeaturedProject.DoesNotExist:
            return error_response(
                errors={'detail': 'Featured project not found'},
                message="Featured project not found",
                status_code=404
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to delete featured project"
            )


class TestimonialsDisplayView(APIView):
    """
    Get testimonials for homepage display.
    Public access only.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: TestimonialDisplaySerializer(many=True)},
        description="Get active testimonials for homepage display (public access)"
    )
    def get(self, request):
        try:
            limit = int(request.query_params.get('limit', 10))
            limit = min(limit, 20)  # Max 20 testimonials

            testimonials = Testimonial.objects.filter(
                is_active=True,
                is_deleted=False
            ).select_related('project').order_by('display_order', '-created_at')[:limit]

            serializer = TestimonialDisplaySerializer(testimonials, many=True)
            return success_response(
                data=serializer.data,
                message=f"Retrieved {testimonials.count()} testimonials"
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to retrieve testimonials"
            )


class CompleteHomePageView(APIView):
    """
    Get complete homepage data in a single optimized API call.
    Includes hero section, statistics, footer, featured projects, and testimonials.
    Public access.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: CompleteHomePageSerializer},
        description="Get complete homepage data in single call (public access)"
    )
    def get(self, request):
        try:
            content = HomePageContent.get_current()
            serializer = CompleteHomePageSerializer(content)
            return success_response(
                data=serializer.data,
                message="Complete homepage data retrieved successfully"
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to retrieve homepage data"
            )


class PageHeroImagesView(APIView):
    """
    Get or update hero images for Projects, About, and Contact pages.
    GET: Public access
    PUT: Admin only
    """

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]

    @extend_schema(
        responses={200: PageHeroImagesSerializer},
        description="Get page hero images (public access)"
    )
    def get(self, request):
        try:
            images = PageHeroImages.get_current()
            serializer = PageHeroImagesSerializer(images, context={'request': request})
            return success_response(
                data=serializer.data,
                message="Page hero images retrieved successfully"
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to retrieve page hero images"
            )

    @extend_schema(
        request=PageHeroImagesSerializer,
        responses={200: PageHeroImagesSerializer},
        description="Update page hero images (admin only)"
    )
    def put(self, request):
        try:
            images = PageHeroImages.get_current()
            serializer = PageHeroImagesSerializer(images, data=request.data, partial=True, context={'request': request})

            if serializer.is_valid():
                serializer.save()
                return success_response(
                    data=serializer.data,
                    message="Page hero images updated successfully"
                )

            return error_response(
                errors=serializer.errors,
                message="Failed to update page hero images"
            )
        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to update page hero images"
            )
