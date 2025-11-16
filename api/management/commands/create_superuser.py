from django.core.management.base import BaseCommand
from decouple import config
from api.models import AdminUser


class Command(BaseCommand):
    help = 'Create initial superuser from environment variables'

    def handle(self, *args, **kwargs):
        email = config('ADMIN_EMAIL', default='admin@hsrgreenhomes.com')
        password = config('ADMIN_PASSWORD', default='admin123')
        full_name = config('ADMIN_NAME', default='HSR Admin')

        if not AdminUser.objects.filter(email=email).exists():
            AdminUser.objects.create_superuser(
                email=email,
                password=password,
                full_name=full_name,
                role='Super Admin'
            )
            self.stdout.write(self.style.SUCCESS(f'Superuser created: {email}'))
        else:
            self.stdout.write(self.style.WARNING(f'Superuser already exists: {email}'))
