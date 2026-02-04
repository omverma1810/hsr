
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.models import AdminUser

def create_admin():
    email = 'admin@hsrgreenhomes.com'
    password = 'Admin@123'
    
    try:
        user = AdminUser.objects.filter(email=email).first()
        if user:
            print(f"User {email} already exists. Updating password.")
            user.set_password(password)
            user.save()
        else:
            print(f"Creating user {email}.")
            AdminUser.objects.create_superuser(email=email, password=password, full_name="Super Admin")
            
        print("Admin user setup complete.")
        print(f"Email: {email}")
        print(f"Password: {password}")
        
    except Exception as e:
        print(f"Error creating admin user: {e}")

if __name__ == '__main__':
    create_admin()
