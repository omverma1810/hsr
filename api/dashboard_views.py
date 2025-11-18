from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample, OpenApiParameter

from .models import Project, Lead, Testimonial, SystemStatus
from .dashboard_serializers import (
    DashboardOverviewSerializer,
    DashboardStatsSerializer,
    RecentLeadSerializer,
    SystemStatusSerializer,
    ProjectStatusBreakdownSerializer,
    LeadStatusBreakdownSerializer
)
from .utils import success_response, error_response
from .permissions import IsAdminUser


class DashboardOverviewView(APIView):
    """
    Complete dashboard overview with all statistics, recent leads, and system status.
    This is the main endpoint for the admin dashboard.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(
        responses={
            200: OpenApiResponse(description='Dashboard overview retrieved successfully - Returns complete dashboard data including statistics, recent leads, system status, and analytics breakdowns in a single optimized call.'),
            401: OpenApiResponse(description='Unauthorized - Invalid or expired token.'),
            403: OpenApiResponse(description='Forbidden - Admin access required.'),
        },
        description='''
        **Complete Dashboard Overview**
        
        Get all dashboard data in a single API call. This is the main endpoint for the admin dashboard page.
        
        **Response includes:**
        - **Statistics**: Total projects (upcoming, ongoing, completed), total leads (new, contacted, qualified, closed)
        - **Recent Leads**: Last 3 leads with project information
        - **System Status**: Current system operational status
        - **Analytics**: Project breakdown by status, lead breakdown by status with percentages
        
        **Use Cases:**
        - Load admin dashboard page
        - Display key metrics and statistics
        - Show recent activity
        - Display system health
        
        **Performance:** This endpoint is optimized to fetch all dashboard data in one call, reducing the number of API requests needed.
        
        **Authentication Required:** Yes (Admin only)
        ''',
        tags=['Dashboard']
    )
    def get(self, request):
        try:
            # Calculate statistics
            total_projects = Project.objects.filter(is_deleted=False).count()
            upcoming_projects = Project.objects.filter(status='upcoming', is_deleted=False).count()
            ongoing_projects = Project.objects.filter(status='ongoing', is_deleted=False).count()
            completed_projects = Project.objects.filter(status='completed', is_deleted=False).count()

            total_leads = Lead.objects.filter(is_deleted=False).count()
            new_leads = Lead.objects.filter(status='new', is_deleted=False).count()
            contacted_leads = Lead.objects.filter(status='contacted', is_deleted=False).count()
            qualified_leads = Lead.objects.filter(status='qualified', is_deleted=False).count()
            closed_leads = Lead.objects.filter(status='closed', is_deleted=False).count()

            statistics = {
                'total_projects': total_projects,
                'upcoming_projects': upcoming_projects,
                'ongoing_projects': ongoing_projects,
                'completed_projects': completed_projects,
                'total_leads': total_leads,
                'new_leads': new_leads,
                'contacted_leads': contacted_leads,
                'qualified_leads': qualified_leads,
                'closed_leads': closed_leads,
            }

            # Get recent leads (last 3)
            recent_leads = Lead.objects.filter(is_deleted=False).select_related('project').order_by('-created_at')[:3]

            # Get system status
            system_status = SystemStatus.get_current()

            # Project breakdown by status
            project_breakdown = []
            if total_projects > 0:
                for status in ['upcoming', 'ongoing', 'completed']:
                    count = Project.objects.filter(status=status, is_deleted=False).count()
                    percentage = (count / total_projects) * 100 if total_projects > 0 else 0
                    project_breakdown.append({
                        'status': status.capitalize(),
                        'count': count,
                        'percentage': round(percentage, 1)
                    })

            # Lead breakdown by status
            lead_breakdown = []
            if total_leads > 0:
                for status in ['new', 'contacted', 'qualified', 'closed']:
                    count = Lead.objects.filter(status=status, is_deleted=False).count()
                    percentage = (count / total_leads) * 100 if total_leads > 0 else 0
                    lead_breakdown.append({
                        'status': status.capitalize(),
                        'count': count,
                        'percentage': round(percentage, 1)
                    })

            # Prepare response data
            data = {
                'statistics': statistics,
                'recent_leads': RecentLeadSerializer(recent_leads, many=True).data,
                'system_status': SystemStatusSerializer(system_status).data,
                'project_breakdown': project_breakdown,
                'lead_breakdown': lead_breakdown,
            }

            return success_response(
                data=data,
                message="Dashboard data retrieved successfully"
            )

        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to retrieve dashboard data"
            )


class DashboardStatsView(APIView):
    """Get only dashboard statistics (for quick refresh)."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(
        responses={
            200: OpenApiResponse(description='Dashboard statistics retrieved successfully - Returns key metrics including project counts by status and lead counts by status.'),
            401: OpenApiResponse(description='Unauthorized - Invalid or expired token.'),
            403: OpenApiResponse(description='Forbidden - Admin access required.'),
        },
        description='''
        **Dashboard Statistics**
        
        Get dashboard statistics only (for quick refresh without full dashboard data).
        
        **Response includes:**
        - `total_projects`: Total number of active projects
        - `upcoming_projects`: Number of upcoming projects
        - `ongoing_projects`: Number of ongoing projects
        - `completed_projects`: Number of completed projects
        - `total_leads`: Total number of active leads
        - `new_leads`: Number of new leads
        - `contacted_leads`: Number of contacted leads
        - `qualified_leads`: Number of qualified leads
        - `closed_leads`: Number of closed leads
        
        **Use Cases:**
        - Quick statistics refresh on dashboard
        - Display summary cards
        - Update metrics without loading full dashboard
        
        **Authentication Required:** Yes (Admin only)
        ''',
        tags=['Dashboard']
    )
    def get(self, request):
        try:
            statistics = {
                'total_projects': Project.objects.filter(is_deleted=False).count(),
                'upcoming_projects': Project.objects.filter(status='upcoming', is_deleted=False).count(),
                'ongoing_projects': Project.objects.filter(status='ongoing', is_deleted=False).count(),
                'completed_projects': Project.objects.filter(status='completed', is_deleted=False).count(),
                'total_leads': Lead.objects.filter(is_deleted=False).count(),
                'new_leads': Lead.objects.filter(status='new', is_deleted=False).count(),
                'contacted_leads': Lead.objects.filter(status='contacted', is_deleted=False).count(),
                'qualified_leads': Lead.objects.filter(status='qualified', is_deleted=False).count(),
                'closed_leads': Lead.objects.filter(status='closed', is_deleted=False).count(),
            }

            return success_response(
                data=statistics,
                message="Statistics retrieved successfully"
            )

        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to retrieve statistics"
            )


class RecentLeadsView(APIView):
    """Get recent leads with optional limit."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(
        parameters=[
            OpenApiParameter('limit', int, description='Number of recent leads to return (default: 10, max: 50)', required=False),
        ],
        responses={
            200: OpenApiResponse(description='Recent leads retrieved successfully - Returns most recent leads with project information, ordered by creation date (newest first).'),
            401: OpenApiResponse(description='Unauthorized - Invalid or expired token.'),
            403: OpenApiResponse(description='Forbidden - Admin access required.'),
        },
        description='''
        **Recent Leads**
        
        Get recent leads for dashboard display.
        
        **Query Parameters:**
        - `limit` (optional): Number of leads to return (default: 10, maximum: 50)
        
        **Example:** `/api/dashboard/recent-leads/?limit=20`
        
        **Response includes:**
        - Lead ID, name, email, phone
        - Associated project information (if any)
        - Lead status and source
        - Time ago (human-readable relative time)
        
        **Use Cases:**
        - Display recent activity on dashboard
        - Show latest lead submissions
        - Quick access to new inquiries
        
        **Authentication Required:** Yes (Admin only)
        ''',
        tags=['Dashboard']
    )
    def get(self, request):
        try:
            limit = int(request.query_params.get('limit', 10))
            limit = min(limit, 50)  # Max 50 leads

            recent_leads = Lead.objects.filter(
                is_deleted=False
            ).select_related('project').order_by('-created_at')[:limit]

            return success_response(
                data=RecentLeadSerializer(recent_leads, many=True).data,
                message=f"Retrieved {recent_leads.count()} recent leads"
            )

        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to retrieve recent leads"
            )


class SystemStatusView(APIView):
    """Get or update system status."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(
        responses={200: SystemStatusSerializer},
        description="Get current system status"
    )
    def get(self, request):
        try:
            system_status = SystemStatus.get_current()
            return success_response(
                data=SystemStatusSerializer(system_status).data,
                message="System status retrieved successfully"
            )

        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to retrieve system status"
            )

    @extend_schema(
        request=SystemStatusSerializer,
        responses={200: SystemStatusSerializer},
        description="Update system status"
    )
    def put(self, request):
        try:
            system_status = SystemStatus.get_current()
            serializer = SystemStatusSerializer(system_status, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return success_response(
                    data=serializer.data,
                    message="System status updated successfully"
                )

            return error_response(
                errors=serializer.errors,
                message="Failed to update system status"
            )

        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to update system status"
            )


class AnalyticsView(APIView):
    """Get detailed analytics and breakdowns."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(
        responses={200: OpenApiResponse(description="Detailed analytics data")},
        description="Get detailed analytics including trends and breakdowns"
    )
    def get(self, request):
        try:
            # Project analytics
            total_projects = Project.objects.filter(is_deleted=False).count()
            project_breakdown = []

            for status in ['upcoming', 'ongoing', 'completed']:
                count = Project.objects.filter(status=status, is_deleted=False).count()
                percentage = (count / total_projects * 100) if total_projects > 0 else 0
                project_breakdown.append({
                    'status': status.capitalize(),
                    'count': count,
                    'percentage': round(percentage, 1)
                })

            # Lead analytics
            total_leads = Lead.objects.filter(is_deleted=False).count()
            lead_breakdown = []

            for status in ['new', 'contacted', 'qualified', 'closed']:
                count = Lead.objects.filter(status=status, is_deleted=False).count()
                percentage = (count / total_leads * 100) if total_leads > 0 else 0
                lead_breakdown.append({
                    'status': status.capitalize(),
                    'count': count,
                    'percentage': round(percentage, 1)
                })

            # Recent activity (last 7 days)
            seven_days_ago = timezone.now() - timedelta(days=7)
            recent_leads_count = Lead.objects.filter(
                created_at__gte=seven_days_ago,
                is_deleted=False
            ).count()

            # Lead sources breakdown
            lead_sources = Lead.objects.filter(
                is_deleted=False
            ).values('source').annotate(count=Count('id'))

            data = {
                'project_breakdown': project_breakdown,
                'lead_breakdown': lead_breakdown,
                'recent_activity': {
                    'leads_last_7_days': recent_leads_count,
                },
                'lead_sources': list(lead_sources),
                'total_projects': total_projects,
                'total_leads': total_leads,
            }

            return success_response(
                data=data,
                message="Analytics retrieved successfully"
            )

        except Exception as e:
            return error_response(
                errors={'detail': str(e)},
                message="Failed to retrieve analytics"
            )
