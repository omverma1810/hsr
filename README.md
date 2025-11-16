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

## Phase 1 Endpoints

### Authentication
- `POST /api/auth/login/` - Admin login
- `POST /api/auth/logout/` - Admin logout
- `POST /api/auth/refresh/` - Refresh JWT token
- `GET /api/auth/me/` - Get current user
- `PUT /api/auth/change-password/` - Change password

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

## Next Phases

- Phase 2: Dashboard & Analytics
- Phase 3: Home Page Content Management
- Phase 4: Projects Management
- Phase 5: Testimonials & Leads Management
- Phase 6: Contact Settings & System Configuration
