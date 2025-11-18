from django.core.management.base import BaseCommand
from api.models import AdminUser


class Command(BaseCommand):
    help = 'Create an additional superuser interactively'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email address for the superuser',
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Password for the superuser',
        )
        parser.add_argument(
            '--full-name',
            type=str,
            help='Full name for the superuser',
        )
        parser.add_argument(
            '--non-interactive',
            action='store_true',
            help='Run in non-interactive mode (requires --email, --password, --full-name)',
        )

    def handle(self, *args, **options):
        email = options.get('email')
        password = options.get('password')
        full_name = options.get('full_name')
        non_interactive = options.get('non_interactive', False)

        # Interactive mode
        if not non_interactive:
            if not email:
                email = input('Email address: ').strip()
            if not password:
                password = input('Password: ').strip()
                password_confirm = input('Password (again): ').strip()
                if password != password_confirm:
                    self.stdout.write(self.style.ERROR('Passwords do not match'))
                    return
            if not full_name:
                full_name = input('Full name: ').strip()

        # Validation
        if not email:
            self.stdout.write(self.style.ERROR('Email is required'))
            return
        if not password:
            self.stdout.write(self.style.ERROR('Password is required'))
            return
        if not full_name:
            self.stdout.write(self.style.ERROR('Full name is required'))
            return

        # Check if user already exists
        if AdminUser.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'User with email {email} already exists'))
            return

        # Create superuser
        try:
            AdminUser.objects.create_superuser(
                email=email,
                password=password,
                full_name=full_name,
                role='Super Admin'
            )
            self.stdout.write(self.style.SUCCESS(f'Superuser created successfully: {email}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating superuser: {str(e)}'))

