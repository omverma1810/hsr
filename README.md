# HSR Green Homes - Backend API

Comprehensive Django REST API for HSR Green Homes admin panel and website management.

## Setup Instructions

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd hsr
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Create `.env` file in root directory (copy from `.env.example`)

### 5. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser
```bash
python manage.py create_superuser
```

### 7. Run Development Server
```bash
python manage.py runserver
```

## API Documentation

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Schema**: http://localhost:8000/api/schema/

## Phase 1 Endpoints (Authentication)

### Authentication
- `POST /api/auth/login/` - Admin login
- `POST /api/auth/logout/` - Admin logout
- `POST /api/auth/refresh/` - Refresh JWT token
- `GET /api/auth/me/` - Get current user
- `PUT /api/auth/change-password/` - Change password

## Phase 2 Endpoints (Dashboard & Analytics)

### Dashboard
- `GET /api/dashboard/` - Complete dashboard overview (stats + recent leads + system status + breakdowns)
- `GET /api/dashboard/stats/` - Dashboard statistics only (for quick refresh)
- `GET /api/dashboard/recent-leads/?limit=10` - Recent leads (default: 10, max: 50)
- `GET /api/dashboard/system-status/` - Get system status
- `PUT /api/dashboard/system-status/` - Update system status
- `GET /api/dashboard/analytics/` - Detailed analytics and breakdowns

## Phase 3 Endpoints (Home Page Content Management)

### Homepage Content
- `GET /api/homepage/` - **Complete homepage data in single call** (public access) - Optimized endpoint with hero, statistics, footer, featured projects, and testimonials
- `GET /api/homepage/content/` - Get complete home page content (public)
- `PUT /api/homepage/content/` - Update home page content (admin only)

### Hero Section
- `GET /api/homepage/hero/` - Get hero section (public)
- `PUT /api/homepage/hero/` - Update hero section (admin only)

### Statistics Section
- `GET /api/homepage/statistics/` - Get statistics section (public)
- `PUT /api/homepage/statistics/` - Update statistics section (admin only)

### Footer Information
- `GET /api/homepage/footer/` - Get footer information (public)
- `PUT /api/homepage/footer/` - Update footer information (admin only)

### Featured Projects
- `GET /api/homepage/featured-projects/` - Get all active featured projects (public)
- `GET /api/homepage/featured-projects/?all=true` - Get all featured projects including inactive (admin only)
- `POST /api/homepage/featured-projects/` - Add a new featured project (admin only)
- `GET /api/homepage/featured-projects/{id}/` - Get specific featured project (admin only)
- `PUT /api/homepage/featured-projects/{id}/` - Update featured project (admin only)
- `DELETE /api/homepage/featured-projects/{id}/` - Remove featured project (admin only)

### Testimonials
- `GET /api/homepage/testimonials/?limit=10` - Get active testimonials for homepage (public, default: 10, max: 20)

### Complete Homepage Response Example
```json
{
  "success": true,
  "message": "Complete homepage data retrieved successfully",
  "data": {
    "hero_section": {
      "hero_title": "Premium Living Spaces in Karimnagar",
      "hero_subtitle": "Discover your dream home with HSR Green Homes - where quality meets comfort",
      "hero_background_image": null,
      "hero_cta_button_text": "Explore Projects"
    },
    "statistics": {
      "experience": {"value": "15+", "label": "Years of Excellence"},
      "projects": {"value": "50+", "label": "Projects Completed"},
      "families": {"value": "2000+", "label": "Happy Families"},
      "sqft": {"value": "10L+", "label": "Sq.Ft Delivered"}
    },
    "footer": {
      "footer_office_address": "HSR Green Homes, Karimnagar, Telangana 505001",
      "footer_phone_number": "+91 9876543210",
      "footer_email": "info@hsrgreenhomes.com",
      "footer_whatsapp_number": "+91 9876543210"
    },
    "featured_projects": [
      {
        "id": 1,
        "project": {
          "id": 1,
          "title": "Green Valley Phase 2",
          "location": "Karimnagar, Telangana",
          "rera_number": "P02400004567",
          "description": "Premium 2BHK and 3BHK apartments",
          "status": "upcoming",
          "hero_image": null
        },
        "display_order": 1,
        "is_active": true
      }
    ],
    "testimonials": [
      {
        "id": 1,
        "customer_name": "Rajesh Kumar",
        "project_title": "Green Valley Phase 2",
        "project_location": "Karimnagar, Telangana",
        "quote": "HSR Green Homes delivered exactly what they promised...",
        "customer_photo": null,
        "display_order": 1
      }
    ]
  }
}
```

### Dashboard Response Example
```json
{
  "success": true,
  "message": "Dashboard data retrieved successfully",
  "data": {
    "statistics": {
      "total_projects": 3,
      "upcoming_projects": 1,
      "ongoing_projects": 1,
      "completed_projects": 1,
      "total_leads": 3,
      "new_leads": 2,
      "contacted_leads": 1,
      "qualified_leads": 0,
      "closed_leads": 0
    },
    "recent_leads": [
      {
        "id": 1,
        "name": "Rajesh Kumar",
        "email": "rajesh.kumar@email.com",
        "phone": "+919876543210",
        "project_name": "Green Valley Phase 2",
        "message": "Interested in 2BHK apartment",
        "status": "new",
        "created_at": "2025-11-16T10:30:00Z",
        "time_ago": "2 hours ago"
      }
    ],
    "system_status": {
      "website_status": true,
      "website_status_display": "Online",
      "whatsapp_integration_active": true,
      "whatsapp_status_display": "Active",
      "contact_forms_working": true,
      "contact_forms_display": "Working",
      "last_backup_at": "2025-11-16T03:00:00Z",
      "last_backup_display": "Today, 3:00 AM"
    },
    "project_breakdown": [
      {"status": "Upcoming", "count": 1, "percentage": 33.3},
      {"status": "Ongoing", "count": 1, "percentage": 33.3},
      {"status": "Completed", "count": 1, "percentage": 33.3}
    ],
    "lead_breakdown": [
      {"status": "New", "count": 2, "percentage": 66.7},
      {"status": "Contacted", "count": 1, "percentage": 33.3},
      {"status": "Qualified", "count": 0, "percentage": 0.0},
      {"status": "Closed", "count": 0, "percentage": 0.0}
    ]
  }
}
```

## Testing

Test login:
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@hsrgreenhomes.com", "password": "admin123"}'
```

## Project Structure
```
hsr/
├── config/          # Django settings and configuration
├── api/             # Main API application
│   ├── models.py    # Database models
│   ├── views.py     # API views
│   ├── serializers.py  # DRF serializers
│   ├── urls.py      # API URL routing
│   ├── permissions.py  # Custom permissions
│   ├── utils.py     # Utility functions
│   └── management/  # Management commands
├── media/           # Uploaded files
├── .env             # Environment variables
└── requirements.txt # Python dependencies
```

## Environment Variables

See `.env.example` for all available configuration options.

## Development Phases

- ✅ Phase 1: Authentication & Core Infrastructure (Complete)
- ✅ Phase 2: Dashboard & Analytics (Complete)
- ✅ Phase 3: Home Page Content Management (Complete)
- Phase 4: Projects Management
- Phase 5: Testimonials & Leads Management
- Phase 6: Contact Settings & System Configuration

## Sample Data

To create sample data for testing:
```bash
python manage.py create_sample_data
```

This creates:
- 3 sample projects (1 upcoming, 1 ongoing, 1 completed)
- 3 sample leads with different statuses
- 3 sample testimonials
- System status record

To initialize homepage content:
```bash
python manage.py setup_homepage
```

This creates the home page content singleton with default values for hero section, statistics, and footer information.
