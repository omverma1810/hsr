from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

# Import existing views
from .views import LoginView, LogoutView, CurrentUserView, ChangePasswordView, PingView

# Import dashboard views (Phase 2)
from .dashboard_views import (
    DashboardOverviewView,
    DashboardStatsView,
    RecentLeadsView,
    SystemStatusView as DashboardSystemStatusView,
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

# Import testimonial views (Phase 5)
from .testimonial_views import (
    TestimonialsListView,
    TestimonialDetailView,
    TestimonialRestoreView,
    BulkTestimonialActionsView
)

# Import lead views (Phase 5)
from .lead_views import (
    LeadsListView,
    LeadDetailView,
    LeadStatusUpdateView,
    LeadAddNoteView,
    LeadRestoreView,
    LeadStatisticsView,
    BulkLeadActionsView,
    ExportLeadsView
)

# Import contact settings views (Phase 6)
from .contact_views import (
    ContactSettingsView,
    WhatsAppConfigView,
    PhoneNumbersView,
    EmailSettingsView,
    AddressMapView,
    SocialMediaView,
    PublicContactInfoView,
    SystemStatusView,
    TriggerBackupView
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
    path('dashboard/system-status/', DashboardSystemStatusView.as_view(), name='dashboard_system_status'),
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

    # Testimonial endpoints (Phase 5)
    path('testimonials/', TestimonialsListView.as_view(), name='testimonials_list'),
    path('testimonials/<int:pk>/', TestimonialDetailView.as_view(), name='testimonial_detail'),
    path('testimonials/<int:pk>/restore/', TestimonialRestoreView.as_view(), name='testimonial_restore'),
    path('testimonials/bulk-actions/', BulkTestimonialActionsView.as_view(), name='testimonial_bulk_actions'),

    # Lead endpoints (Phase 5)
    path('leads/', LeadsListView.as_view(), name='leads_list'),
    path('leads/<int:pk>/', LeadDetailView.as_view(), name='lead_detail'),
    path('leads/<int:pk>/status/', LeadStatusUpdateView.as_view(), name='lead_status_update'),
    path('leads/<int:pk>/notes/', LeadAddNoteView.as_view(), name='lead_add_note'),
    path('leads/<int:pk>/restore/', LeadRestoreView.as_view(), name='lead_restore'),
    path('leads/statistics/', LeadStatisticsView.as_view(), name='lead_statistics'),
    path('leads/bulk-actions/', BulkLeadActionsView.as_view(), name='lead_bulk_actions'),
    path('leads/export/', ExportLeadsView.as_view(), name='leads_export'),

    # Contact Settings & System Configuration endpoints (Phase 6)
    # Complete contact settings
    path('contact-settings/', ContactSettingsView.as_view(), name='contact_settings'),

    # Individual contact setting sections
    path('contact-settings/whatsapp/', WhatsAppConfigView.as_view(), name='whatsapp_config'),
    path('contact-settings/phone/', PhoneNumbersView.as_view(), name='phone_numbers'),
    path('contact-settings/email/', EmailSettingsView.as_view(), name='email_settings'),
    path('contact-settings/address/', AddressMapView.as_view(), name='address_map'),
    path('contact-settings/social-media/', SocialMediaView.as_view(), name='social_media'),

    # Public contact info (optimized)
    path('contact-info/', PublicContactInfoView.as_view(), name='public_contact_info'),

    # System configuration
    path('system/', SystemStatusView.as_view(), name='system_status'),
    path('system/backup/', TriggerBackupView.as_view(), name='trigger_backup'),
]
