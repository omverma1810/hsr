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

## Phase 4 Endpoints (Projects Management - Full CRUD)

### Main Project CRUD
- `GET /api/projects/` - List all projects (public, with filtering, search, sort, pagination)
- `POST /api/projects/` - Create new project (admin)
- `GET /api/projects/{id}/` - Get project details (public, increments view count)
- `PUT /api/projects/{id}/` - Update project (admin, partial updates supported)
- `DELETE /api/projects/{id}/` - Delete project (admin, soft delete)

### Query Parameters for Project List
- `status` - Filter by status (upcoming/ongoing/completed)
- `is_featured` - Filter by featured status (true/false)
- `search` - Search in title, location, RERA number, description
- `sort_by` - Sort field (created_at, updated_at, title, status, view_count)
- `sort_order` - Sort direction (asc/desc)
- `page` - Page number
- `page_size` - Items per page (10/25/50/100)
- `include_deleted` - Include soft-deleted projects (admin only)

### Gallery Management
- `GET /api/projects/{id}/gallery/` - Get all gallery images
- `POST /api/projects/{id}/gallery/` - Add gallery image
- `PUT /api/projects/{id}/gallery/{image_id}/` - Update gallery image
- `DELETE /api/projects/{id}/gallery/{image_id}/` - Delete gallery image

### Floor Plans Management
- `GET /api/projects/{id}/floor-plans/` - Get all floor plans
- `POST /api/projects/{id}/floor-plans/` - Add floor plan
- `PUT /api/projects/{id}/floor-plans/{plan_id}/` - Update floor plan
- `DELETE /api/projects/{id}/floor-plans/{plan_id}/` - Delete floor plan

### Project Actions
- `POST /api/projects/{id}/restore/` - Restore soft-deleted project
- `POST /api/projects/{id}/clone/` - Clone/duplicate project

### Bulk Actions
- `POST /api/projects/bulk-actions/` - Perform bulk actions
  - Actions: delete, restore, feature, unfeature, change_status
  - Body: `{"project_ids": [1,2,3], "action": "delete"}`

### Export/Import
- `GET /api/projects/export/` - Export projects to CSV

### Reference Data
- `GET /api/projects/configurations/` - Get available configurations (public)
- `GET /api/projects/amenities/` - Get available amenities (public)

### Project Configuration Options
- 1BHK (`1bhk`)
- 2BHK (`2bhk`)
- 3BHK (`3bhk`)
- 4BHK (`4bhk`)
- Villa (`villa`)
- Duplex (`duplex`)

### Project Amenity Options
- Swimming Pool (`swimming_pool`)
- Children's Play Area (`childrens_play_area`)
- Security (`security`)
- Parking (`parking`)
- Jogging Track (`jogging_track`)
- Gym (`gym`)
- Clubhouse (`clubhouse`)
- Power Backup (`power_backup`)
- Garden (`garden`)
- Community Hall (`community_hall`)

### Example: Create Project Request
```json
{
  "title": "Green Valley Phase 3",
  "location": "Karimnagar, Telangana",
  "rera_number": "P02400012345",
  "description": "Premium residential project with modern amenities",
  "status": "upcoming",
  "hero_image_url": "https://example.com/hero.jpg",
  "brochure_url": "https://example.com/brochure.pdf",
  "configurations_list": ["2bhk", "3bhk"],
  "amenities_list": ["swimming_pool", "gym", "parking", "security"],
  "is_featured": true
}
```

### Example: Project Detail Response
```json
{
  "success": true,
  "message": "Project retrieved successfully",
  "data": {
    "id": 1,
    "title": "Green Valley Phase 2",
    "slug": "green-valley-phase-2",
    "location": "Karimnagar, Telangana",
    "rera_number": "P02400004567",
    "description": "Premium residential project...",
    "status": "upcoming",
    "hero_image": "https://example.com/hero.jpg",
    "brochure": "https://example.com/brochure.pdf",
    "configurations": {"2bhk": true, "3bhk": true},
    "configurations_list": ["2bhk", "3bhk"],
    "amenities": {"swimming_pool": true, "gym": true},
    "amenities_list": ["swimming_pool", "gym"],
    "is_featured": true,
    "view_count": 150,
    "gallery_images": [
      {
        "id": 1,
        "image": "https://example.com/gallery1.jpg",
        "caption": "Exterior View",
        "display_order": 1
      }
    ],
    "floor_plans": [
      {
        "id": 1,
        "title": "2BHK Floor Plan",
        "file_path": "https://example.com/2bhk-plan.pdf",
        "display_order": 1
      }
    ],
    "leads_count": 5,
    "testimonials_count": 2,
    "created_by_name": "HSR Admin",
    "created_at": "2025-11-16T10:00:00Z"
  }
}
```

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

## Phase 5 Endpoints (Testimonials & Leads Management)

### Testimonials Management
- `GET /api/testimonials/` - List all testimonials (admin, with filtering, search, sort, pagination)
- `POST /api/testimonials/` - Create new testimonial (admin only)
- `GET /api/testimonials/{id}/` - Get testimonial details (admin only)
- `PUT /api/testimonials/{id}/` - Update testimonial (admin only, partial updates supported)
- `DELETE /api/testimonials/{id}/` - Delete testimonial (admin only, soft delete)
- `POST /api/testimonials/{id}/restore/` - Restore soft-deleted testimonial (admin only)
- `POST /api/testimonials/bulk-actions/` - Perform bulk actions (admin only)
  - Actions: delete, restore, activate, deactivate, verify, unverify
  - Body: `{"testimonial_ids": [1,2,3], "action": "verify"}`

### Query Parameters for Testimonial List
- `project` - Filter by project ID
- `is_active` - Filter by active status (true/false)
- `verified` - Filter by verified status (true/false)
- `min_rating` - Filter by minimum rating (1-5)
- `search` - Search in customer name, quote, project title
- `sort_by` - Sort field (created_at, rating, display_order, customer_name)
- `page` - Page number
- `page_size` - Items per page (10/25/50/100)

### Leads Management
- `GET /api/leads/` - List all leads (admin only, with filtering, search, sort, pagination)
- `POST /api/leads/` - Create new lead (public - contact form submission)
- `GET /api/leads/{id}/` - Get lead details (admin only)
- `PUT /api/leads/{id}/` - Update lead (admin only, partial updates supported)
- `DELETE /api/leads/{id}/` - Delete lead (admin only, soft delete)
- `POST /api/leads/{id}/status/` - Update lead status with tracking (admin only)
- `POST /api/leads/{id}/notes/` - Add note to lead (admin only)
- `POST /api/leads/{id}/restore/` - Restore soft-deleted lead (admin only)
- `GET /api/leads/statistics/` - Get lead statistics and analytics (admin only)
- `POST /api/leads/bulk-actions/` - Perform bulk actions (admin only)
  - Actions: delete, restore, change_status, change_priority, assign_contact
  - Body: `{"lead_ids": [1,2,3], "action": "change_status", "status": "qualified"}`
- `GET /api/leads/export/` - Export leads to CSV (admin only)

### Query Parameters for Lead List
- `status` - Filter by status (new/contacted/qualified/closed)
- `priority` - Filter by priority (low/medium/high/urgent)
- `source` - Filter by source (contact_form/whatsapp/phone_call/walk_in)
- `project` - Filter by project ID
- `contacted_by` - Filter by admin user ID
- `overdue_only` - Show only overdue follow-ups (true/false)
- `search` - Search in name, email, phone, message, project title
- `sort_by` - Sort field (created_at, priority, status, next_follow_up, name)
- `page` - Page number
- `page_size` - Items per page (10/25/50/100)

### Example: Create Testimonial Request
```json
{
  "customer_name": "Rajesh Kumar",
  "project": 1,
  "quote": "Excellent service and quality construction. Very happy with my new home!",
  "rating": 5,
  "verified": true,
  "is_active": true,
  "display_order": 1
}
```

### Example: Testimonial Detail Response
```json
{
  "success": true,
  "message": "Testimonial retrieved successfully",
  "data": {
    "id": 1,
    "customer_name": "Rajesh Kumar",
    "project": 1,
    "project_title": "Green Valley Phase 2",
    "project_location": "Karimnagar, Telangana",
    "project_status": "upcoming",
    "quote": "Excellent service and quality construction. Very happy with my new home!",
    "customer_photo": null,
    "rating": 5,
    "rating_stars": "★★★★★",
    "verified": true,
    "is_active": true,
    "display_order": 1,
    "created_at": "2025-11-16T10:00:00Z",
    "updated_at": "2025-11-16T10:00:00Z"
  }
}
```

### Example: Create Lead Request (Public Contact Form)
```json
{
  "name": "Priya Sharma",
  "email": "priya@example.com",
  "phone": "+919876543210",
  "project": 1,
  "message": "I am interested in 2BHK apartments. Please contact me.",
  "source": "contact_form",
  "preferred_contact_method": "phone"
}
```

### Example: Lead Detail Response
```json
{
  "success": true,
  "message": "Lead retrieved successfully",
  "data": {
    "id": 1,
    "name": "Priya Sharma",
    "email": "priya@example.com",
    "phone": "+919876543210",
    "project": 1,
    "project_title": "Green Valley Phase 2",
    "project_location": "Karimnagar, Telangana",
    "message": "I am interested in 2BHK apartments. Please contact me.",
    "status": "contacted",
    "status_color": "#F59E0B",
    "priority": "medium",
    "priority_color": "#F59E0B",
    "source": "contact_form",
    "preferred_contact_method": "phone",
    "next_follow_up": "2025-11-18T10:00:00Z",
    "follow_up_count": 2,
    "contacted_at": "2025-11-16T11:00:00Z",
    "contacted_by": 1,
    "contacted_by_name": "HSR Admin",
    "contacted_by_email": "admin@hsrgreenhomes.com",
    "notes": "\n[2025-11-16 11:00:00] HSR Admin: Called customer and discussed 2BHK options\n[2025-11-16 14:30:00] HSR Admin: Sent brochure via email",
    "time_ago": "2 hours ago",
    "is_overdue": false,
    "created_at": "2025-11-16T10:00:00Z",
    "updated_at": "2025-11-16T14:30:00Z"
  }
}
```

### Example: Lead Statistics Response
```json
{
  "success": true,
  "message": "Lead statistics retrieved successfully",
  "data": {
    "total_leads": 45,
    "new_leads": 15,
    "contacted_leads": 20,
    "qualified_leads": 8,
    "closed_leads": 2,
    "contact_rate": 44.44,
    "qualification_rate": 17.78,
    "close_rate": 4.44,
    "urgent_leads": 3,
    "high_priority_leads": 8,
    "medium_priority_leads": 25,
    "low_priority_leads": 9,
    "leads_with_follow_up": 18,
    "overdue_follow_ups": 5,
    "source_breakdown": {
      "contact_form": 28,
      "whatsapp": 10,
      "phone_call": 5,
      "walk_in": 2
    },
    "leads_today": 3,
    "leads_this_week": 12,
    "leads_this_month": 45
  }
}
```

## Phase 6 Endpoints (Contact Settings & System Configuration)

### Contact Settings Management

#### Complete Contact Settings
- `GET /api/contact-settings/` - Get complete contact settings (public access with full data)
- `PUT /api/contact-settings/` - Update contact settings (admin only, partial updates supported)

#### Individual Setting Sections
- `GET /api/contact-settings/whatsapp/` - Get WhatsApp configuration (public)
- `PUT /api/contact-settings/whatsapp/` - Update WhatsApp configuration (admin only)
- `GET /api/contact-settings/phone/` - Get phone numbers (public)
- `PUT /api/contact-settings/phone/` - Update phone numbers (admin only)
- `GET /api/contact-settings/email/` - Get email settings (public)
- `PUT /api/contact-settings/email/` - Update email settings (admin only)
- `GET /api/contact-settings/address/` - Get office address and map (public)
- `PUT /api/contact-settings/address/` - Update office address and map (admin only)
- `GET /api/contact-settings/social-media/` - Get social media links (public)
- `PUT /api/contact-settings/social-media/` - Update social media links (admin only)

#### Optimized Public Contact Info
- `GET /api/contact-info/` - **Get all contact information in single call** (public access) - Optimized endpoint with WhatsApp, phone, email, address, and social media

### System Configuration
- `GET /api/system/` - Get system status and configuration (public: limited data, admin: full data)
- `PUT /api/system/` - Update system status and configuration (admin only)
- `POST /api/system/backup/` - Trigger manual backup (admin only)

### Example: WhatsApp Configuration Response
```json
{
  "success": true,
  "message": "WhatsApp configuration retrieved successfully",
  "data": {
    "whatsapp_enabled": true,
    "whatsapp_number": "+919876543210",
    "whatsapp_business_hours": "9:00 AM - 8:00 PM",
    "whatsapp_auto_reply": "Hello! Thank you for contacting HSR Green Homes. We will get back to you shortly."
  }
}
```

### Example: Public Contact Info Response (Complete)
```json
{
  "success": true,
  "message": "Public contact information retrieved successfully",
  "data": {
    "whatsapp": {
      "number": "+919876543210",
      "business_hours": "9:00 AM - 8:00 PM"
    },
    "phone": {
      "primary": "+919876543210",
      "secondary": "+919876543211",
      "toll_free": "1800-123-4567",
      "business_hours": "9:00 AM - 6:00 PM (Mon-Sat)"
    },
    "email": {
      "info": "info@hsrgreenhomes.com",
      "sales": "sales@hsrgreenhomes.com",
      "support": "support@hsrgreenhomes.com"
    },
    "address": {
      "street": "HSR Green Homes Building",
      "area": "Bommakal",
      "city": "Karimnagar",
      "state": "Telangana",
      "pincode": "505001",
      "country": "India",
      "full_address": "HSR Green Homes Building, Bommakal, Karimnagar, Telangana, 505001, India",
      "map_embed": "https://maps.google.com/embed/..."
    },
    "social_media": {
      "facebook": "https://facebook.com/hsrgreenhomes",
      "instagram": "https://instagram.com/hsrgreenhomes",
      "twitter": "https://twitter.com/hsrgreenhomes",
      "linkedin": "https://linkedin.com/company/hsrgreenhomes",
      "youtube": "https://youtube.com/@hsrgreenhomes"
    }
  }
}
```

### Example: Update Contact Settings Request
```json
{
  "whatsapp_enabled": true,
  "whatsapp_number": "+919876543210",
  "primary_phone": "+919876543210",
  "info_email": "info@hsrgreenhomes.com",
  "city": "Karimnagar",
  "facebook_url": "https://facebook.com/hsrgreenhomes"
}
```

### Example: System Status Response (Admin)
```json
{
  "success": true,
  "message": "System status retrieved successfully",
  "data": {
    "id": 1,
    "site_name": "HSR Green Homes",
    "site_url": "https://hsrgreenhomes.com",
    "website_status": true,
    "whatsapp_integration_active": true,
    "contact_forms_working": true,
    "last_backup_at": "2025-11-16T03:00:00Z",
    "auto_backup_enabled": true,
    "session_timeout": 30,
    "maintenance_mode": false,
    "maintenance_message": "We are currently performing maintenance. Please check back soon.",
    "email_notifications_enabled": true,
    "notification_email": "admin@hsrgreenhomes.com",
    "meta_title": "HSR Green Homes - Premium Real Estate in Karimnagar",
    "meta_description": "Discover premium residential projects in Karimnagar with HSR Green Homes",
    "meta_keywords": "real estate, karimnagar, residential projects, apartments",
    "uptime_status": {
      "website": "Online",
      "whatsapp": "Active",
      "forms": "Working",
      "maintenance": "Disabled"
    },
    "created_at": "2025-11-16T00:00:00Z",
    "updated_at": "2025-11-16T10:00:00Z"
  }
}
```

### Example: System Status Response (Public - Limited)
```json
{
  "success": true,
  "message": "System status retrieved successfully",
  "data": {
    "site_name": "HSR Green Homes",
    "maintenance_mode": false,
    "maintenance_message": null
  }
}
```

### Example: Trigger Backup Request
```bash
curl -X POST http://localhost:8000/api/system/backup/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Response:
```json
{
  "success": true,
  "message": "Backup triggered successfully",
  "data": {
    "message": "Backup triggered successfully",
    "timestamp": "2025-11-16T15:30:00Z"
  }
}
```

### Initialize Contact Settings
```bash
python manage.py setup_contact_settings
```

This creates the contact settings and system status singletons with default values for all contact information and system configuration.

## Development Phases

- ✅ Phase 1: Authentication & Core Infrastructure (Complete)
- ✅ Phase 2: Dashboard & Analytics (Complete)
- ✅ Phase 3: Home Page Content Management (Complete)
- ✅ Phase 4: Projects Management - Full CRUD (Complete)
- ✅ Phase 5: Testimonials & Leads Management (Complete)
- ✅ Phase 6: Contact Settings & System Configuration (Complete)

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

To create sample projects with complete data (gallery images, floor plans, configurations, amenities):
```bash
python manage.py create_sample_projects
```

This creates:
- 5 sample projects with complete data
- Gallery images for each project (3 images per project)
- Floor plans for each project (up to 2 floor plans)
- Configurations (1BHK, 2BHK, 3BHK, 4BHK, Villa, Duplex)
- Amenities (Swimming Pool, Gym, Parking, etc.)
