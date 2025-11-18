from django.core.management.base import BaseCommand
from api.models import AdminUser


class Command(BaseCommand):
    help = 'Create a dummy test user for API testing'

    def handle(self, *args, **kwargs):
        email = "dummy@test.com"
        password = "DummyTest123!"
        full_name = "Dummy Test User"
        
        # Delete if exists
        deleted_count, _ = AdminUser.objects.filter(email=email).delete()
        if deleted_count > 0:
            self.stdout.write(self.style.WARNING(f'Deleted existing user: {email}'))
        
        # Create new user
        user = AdminUser.objects.create_superuser(
            email=email,
            password=password,
            full_name=full_name,
            role='Test Admin'
        )
        
        self.stdout.write(self.style.SUCCESS(f'✅ Dummy user created successfully!'))
        self.stdout.write(f'   Email: {email}')
        self.stdout.write(f'   Password: {password}')
        self.stdout.write(f'   Full Name: {full_name}')
        self.stdout.write(f'   ID: {user.id}')
        self.stdout.write(f'   Is Staff: {user.is_staff}')
        self.stdout.write(f'   Is Superuser: {user.is_superuser}')

