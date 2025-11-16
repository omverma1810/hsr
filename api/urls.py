from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

# Import existing views
from .views import LoginView, LogoutView, CurrentUserView, ChangePasswordView, PingView

# Import dashboard views (Phase 2)
from .dashboard_views import (
    DashboardOverviewView,
    DashboardStatsView,
    RecentLeadsView,
    SystemStatusView,
    AnalyticsView
)

# Import homepage views (Phase 3)
from .homepage_views import (
    HomePageContentView,
    HeroSectionView,
    StatisticsSectionView,
    FooterInfoView,
    FeaturedProjectsListView,
    FeaturedProjectDetailView,
    TestimonialsDisplayView,
    CompleteHomePageView
)

# Import project views (Phase 4)
from .project_views import (
    ProjectsListView,
    ProjectDetailView,
    ProjectGalleryView,
    ProjectGalleryImageDetailView,
    ProjectFloorPlansView,
    ProjectFloorPlanDetailView,
    ProjectRestoreView,
    ProjectCloneView,
    BulkActionsView,
    ExportProjectsView,
    ConfigurationsListView,
    AmenitiesListView
)

urlpatterns = [
    # Authentication endpoints (Phase 1)
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', CurrentUserView.as_view(), name='current_user'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change_password'),

    # Health-check endpoint
    path('ping/', PingView.as_view(), name='ping'),

    # Dashboard endpoints (Phase 2)
    path('dashboard/', DashboardOverviewView.as_view(), name='dashboard_overview'),
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard_stats'),
    path('dashboard/recent-leads/', RecentLeadsView.as_view(), name='recent_leads'),
    path('dashboard/system-status/', SystemStatusView.as_view(), name='system_status'),
    path('dashboard/analytics/', AnalyticsView.as_view(), name='analytics'),

    # Homepage endpoints (Phase 3)
    path('homepage/', CompleteHomePageView.as_view(), name='complete_homepage'),
    path('homepage/content/', HomePageContentView.as_view(), name='homepage_content'),
    path('homepage/hero/', HeroSectionView.as_view(), name='hero_section'),
    path('homepage/statistics/', StatisticsSectionView.as_view(), name='statistics_section'),
    path('homepage/footer/', FooterInfoView.as_view(), name='footer_info'),
    path('homepage/featured-projects/', FeaturedProjectsListView.as_view(), name='featured_projects_list'),
    path('homepage/featured-projects/<int:pk>/', FeaturedProjectDetailView.as_view(), name='featured_project_detail'),
    path('homepage/testimonials/', TestimonialsDisplayView.as_view(), name='testimonials_display'),

    # Project endpoints (Phase 4)
    # Main project CRUD
    path('projects/', ProjectsListView.as_view(), name='projects_list'),
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project_detail'),

    # Project gallery management
    path('projects/<int:pk>/gallery/', ProjectGalleryView.as_view(), name='project_gallery'),
    path('projects/<int:pk>/gallery/<int:image_id>/', ProjectGalleryImageDetailView.as_view(), name='project_gallery_image_detail'),

    # Project floor plans management
    path('projects/<int:pk>/floor-plans/', ProjectFloorPlansView.as_view(), name='project_floor_plans'),
    path('projects/<int:pk>/floor-plans/<int:plan_id>/', ProjectFloorPlanDetailView.as_view(), name='project_floor_plan_detail'),

    # Project actions
    path('projects/<int:pk>/restore/', ProjectRestoreView.as_view(), name='project_restore'),
    path('projects/<int:pk>/clone/', ProjectCloneView.as_view(), name='project_clone'),

    # Bulk actions
    path('projects/bulk-actions/', BulkActionsView.as_view(), name='project_bulk_actions'),
    path('projects/export/', ExportProjectsView.as_view(), name='projects_export'),

    # Reference data
    path('projects/configurations/', ConfigurationsListView.as_view(), name='configurations_list'),
    path('projects/amenities/', AmenitiesListView.as_view(), name='amenities_list'),
]
