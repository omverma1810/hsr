# 🚨 PRODUCTION DEPLOYMENT CHECKLIST

## BEFORE DEPLOYING - Complete These Steps:

### ✅ Environment Variables (.env)
- [ ] `SECRET_KEY` - Generate a new secure key (NOT the default!)
- [ ] `DEBUG=False`
- [ ] `ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com`
- [ ] `BASE_URL=https://yourdomain.com` (NOT localhost!)
- [ ] `DB_ENGINE=django.db.backends.postgresql`
- [ ] Database credentials (DB_NAME, DB_USER, DB_PASSWORD, etc.)
- [ ] `CORS_ALLOWED_ORIGINS=https://yourdomain.com`

### ✅ Database
- [ ] PostgreSQL installed and running
- [ ] Database created
- [ ] Migrations run: `python manage.py migrate`
- [ ] Superuser created: `python manage.py create_superuser`

### ✅ Static & Media Files
- [ ] Static files collected: `python manage.py collectstatic --noinput`
- [ ] Web server (Nginx/Apache) configured to serve `/static/` and `/media/`
- [ ] OR cloud storage configured for media files

### ✅ Security
- [ ] HTTPS/SSL certificate configured
- [ ] Firewall rules set
- [ ] Strong passwords for all accounts
- [ ] `.env` file is NOT committed to Git (already in .gitignore ✅)

### ✅ Server Setup
- [ ] Application server (Gunicorn/uWSGI) configured
- [ ] Reverse proxy (Nginx) configured
- [ ] Process manager (systemd) configured
- [ ] Logs directory created: `mkdir -p logs`

### ✅ Testing
- [ ] API endpoints work
- [ ] Admin login works
- [ ] Static files load
- [ ] Media files load
- [ ] HTTPS redirects work
- [ ] API docs require authentication (in production)

## ⚠️ CRITICAL WARNINGS

1. **NEVER deploy with `DEBUG=True`** - This exposes sensitive information
2. **NEVER use default `SECRET_KEY`** - Generate a new one
3. **NEVER commit `.env` file** - It contains secrets
4. **NEVER use SQLite in production** - Use PostgreSQL
5. **NEVER serve static/media files with Django** - Use web server or cloud storage

## Quick Commands

```bash
# Generate SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create superuser
python manage.py create_superuser

# Create logs directory
mkdir -p logs
```

## Need Help?

See `PRODUCTION_DEPLOYMENT.md` for detailed instructions.

