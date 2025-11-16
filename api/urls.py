from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

# Import existing views
from .views import LoginView, LogoutView, CurrentUserView, ChangePasswordView

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

urlpatterns = [
    # Authentication endpoints (Phase 1)
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', CurrentUserView.as_view(), name='current_user'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change_password'),

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
]
