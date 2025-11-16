from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

# Import existing views
from .views import LoginView, LogoutView, CurrentUserView, ChangePasswordView

# Import new dashboard views
from .dashboard_views import (
    DashboardOverviewView,
    DashboardStatsView,
    RecentLeadsView,
    SystemStatusView,
    AnalyticsView
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
]
