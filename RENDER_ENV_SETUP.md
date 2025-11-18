# Render Environment Variables Setup Guide

## ✅ Generated SECRET_KEY

Your secure SECRET_KEY has been generated:
```
f#*610wj@51_ol(t^@d(zcqb$g*jyzp5tcfrhkm56p3&r8d4w3
```

## 📋 Step-by-Step: Add Environment Variables to Render

### Step 1: Go to Your Backend Service
1. Open Render Dashboard
2. Click on your backend service (e.g., "HSR")

### Step 2: Navigate to Environment
1. Click on "Environment" tab (left sidebar)
2. Click "Add Environment Variable" button

### Step 3: Add Each Variable

Add these variables one by one (copy-paste from below):

#### Security Variables:
```
SECRET_KEY = f#*610wj@51_ol(t^@d(zcqb$g*jyzp5tcfrhkm56p3&r8d4w3
DEBUG = False
ALLOWED_HOSTS = your-app-name.onrender.com
```
⚠️ **Replace `your-app-name` with your actual Render service name!**

#### CORS:
```
CORS_ALLOWED_ORIGINS = https://your-frontend-domain.com
```
⚠️ **Replace with your frontend domain (Vercel, etc.)**

#### Database (From Your Render PostgreSQL):
```
DB_ENGINE = django.db.backends.postgresql
DB_NAME = hsr_green_homes
DB_USER = [from Render PostgreSQL service]
DB_PASSWORD = [from Render PostgreSQL service]
DB_HOST = [from Render PostgreSQL service]
DB_PORT = 5432
```
📝 **Get these from:** Render Dashboard → Your PostgreSQL Service → "Connections" section

#### Base URL:
```
BASE_URL = https://your-app-name.onrender.com
```
⚠️ **Replace `your-app-name` with your actual Render service name!**

#### Security Settings:
```
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

#### JWT (Optional):
```
JWT_ACCESS_TOKEN_LIFETIME = 60
JWT_REFRESH_TOKEN_LIFETIME = 10080
```

## 🔍 How to Get Database Credentials

1. Go to Render Dashboard
2. Click on your **PostgreSQL** service
3. Scroll to "Connections" section
4. You'll see:
   - **Internal Database URL** (use this if same region)
   - **External Database URL** (for external access)
   - Or individual fields:
     - Host
     - Port
     - Database
     - User
     - Password

Copy each value to the corresponding environment variable.

## ✅ Quick Checklist

- [ ] SECRET_KEY added (use the generated one above)
- [ ] DEBUG=False
- [ ] ALLOWED_HOSTS = your Render service domain
- [ ] CORS_ALLOWED_ORIGINS = your frontend domain
- [ ] Database credentials from Render PostgreSQL
- [ ] BASE_URL = your Render service URL
- [ ] Security settings added (SECURE_SSL_REDIRECT, etc.)

## 🚨 Important Notes

1. **Never commit `.env` file** - It's already in `.gitignore`
2. **SECRET_KEY is sensitive** - Keep it secret, don't share
3. **Replace placeholders** - `your-app-name`, `your-frontend-domain.com`
4. **Database credentials** - Must be from your Render PostgreSQL service
5. **After adding variables** - Render will automatically redeploy

## 📝 Example Values

If your Render service is named `hsr-backend`:
```
ALLOWED_HOSTS = hsr-backend.onrender.com
BASE_URL = https://hsr-backend.onrender.com
```

If your frontend is on Vercel at `hsr-frontend.vercel.app`:
```
CORS_ALLOWED_ORIGINS = https://hsr-frontend.vercel.app,https://*.vercel.app
```

