# Production Deployment Guide

## ⚠️ CRITICAL: Pre-Deployment Checklist

Before deploying to production, ensure you have completed ALL of the following:

### 1. Environment Variables (.env file)

Create a `.env` file in the `hsr-be` directory with the following **REQUIRED** variables:

```env
# Security (CRITICAL - Change these!)
SECRET_KEY=your-super-secret-key-here-generate-a-random-one
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (Use PostgreSQL in production)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=hsr_green_homes
DB_USER=your_db_user
DB_PASSWORD=your_secure_db_password
DB_HOST=localhost
DB_PORT=5432

# Base URL (CRITICAL - Change from localhost!)
BASE_URL=https://yourdomain.com

# CORS (Update with your frontend domain)
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Security Settings (Production)
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# JWT Settings (Optional - adjust as needed)
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=10080
```

### 2. Generate a Secure SECRET_KEY

**NEVER use the default SECRET_KEY in production!**

Generate a secure key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Database Setup

**Use PostgreSQL in production (NOT SQLite):**

1. Install PostgreSQL on your server
2. Create a database and user
3. Update `.env` with database credentials
4. Run migrations:
   ```bash
   python manage.py migrate
   ```

### 4. Static and Media Files

**Django does NOT serve static/media files in production. Use a web server (Nginx/Apache) or cloud storage.**

#### Option A: Nginx (Recommended)
Configure Nginx to serve static and media files:
```nginx
location /static/ {
    alias /path/to/hsr-be/staticfiles/;
}

location /media/ {
    alias /path/to/hsr-be/media/;
}
```

#### Option B: Cloud Storage (AWS S3, etc.)
Configure Django to use cloud storage for media files.

### 5. Collect Static Files

Before deploying, run:
```bash
python manage.py collectstatic --noinput
```

### 6. Create Superuser

```bash
python manage.py create_superuser
```

### 7. Security Checklist

- ✅ `DEBUG=False` in production
- ✅ `SECRET_KEY` is set and secure
- ✅ `ALLOWED_HOSTS` includes your domain
- ✅ `BASE_URL` points to your production domain (HTTPS)
- ✅ Database uses PostgreSQL (not SQLite)
- ✅ HTTPS is enabled (SSL certificate configured)
- ✅ Static/media files served by web server (not Django)
- ✅ API documentation requires authentication
- ✅ CORS is properly configured

### 8. Server Configuration

#### Using Gunicorn (Recommended)

Install:
```bash
pip install gunicorn
```

Run:
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

#### Using uWSGI

Install:
```bash
pip install uwsgi
```

Create `uwsgi.ini`:
```ini
[uwsgi]
module = config.wsgi:application
master = true
processes = 4
socket = /tmp/hsr.sock
chmod-socket = 666
vacuum = true
die-on-term = true
```

### 9. Reverse Proxy (Nginx)

Example Nginx configuration:
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/hsr-be/staticfiles/;
    }

    location /media/ {
        alias /path/to/hsr-be/media/;
    }
}
```

### 10. Logging

Logs will be written to `logs/django.log`. Ensure the directory exists:
```bash
mkdir -p logs
chmod 755 logs
```

### 11. Process Management (Systemd)

Create `/etc/systemd/system/hsr-backend.service`:
```ini
[Unit]
Description=HSR Green Homes Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/hsr-be
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 4

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable hsr-backend
sudo systemctl start hsr-backend
```

## Post-Deployment Verification

1. ✅ Check that `DEBUG=False` is working (no error pages show sensitive info)
2. ✅ Verify HTTPS is working (no mixed content warnings)
3. ✅ Test API endpoints
4. ✅ Verify static files are being served
5. ✅ Verify media files are being served
6. ✅ Check that API docs require authentication
7. ✅ Test admin login
8. ✅ Monitor logs for errors

## Common Issues

### Issue: Static files not loading
**Solution:** Run `python manage.py collectstatic` and ensure web server is configured to serve `/static/`

### Issue: Media files not loading
**Solution:** Ensure web server is configured to serve `/media/` or use cloud storage

### Issue: 500 errors
**Solution:** Check logs in `logs/django.log` and ensure all environment variables are set

### Issue: CORS errors
**Solution:** Update `CORS_ALLOWED_ORIGINS` in `.env` with your frontend domain

### Issue: Database connection errors
**Solution:** Verify PostgreSQL is running and credentials in `.env` are correct

## Monitoring

- Monitor `logs/django.log` for errors
- Set up error tracking (Sentry, etc.)
- Monitor server resources (CPU, memory, disk)
- Set up database backups

## Backup Strategy

1. **Database backups:** Set up automated PostgreSQL backups
2. **Media files:** Backup the `media/` directory regularly
3. **Code:** Use version control (Git) - already done ✅

## Security Best Practices

1. Keep Django and dependencies updated
2. Use strong passwords for database and admin users
3. Regularly rotate JWT tokens (already configured)
4. Monitor for suspicious activity
5. Use a firewall to restrict access
6. Keep server OS updated
7. Use environment variables for all secrets (never commit `.env`)

## Support

If you encounter issues:
1. Check `logs/django.log`
2. Check server logs (Nginx/Apache)
3. Verify all environment variables are set correctly
4. Ensure database is accessible
5. Verify file permissions

