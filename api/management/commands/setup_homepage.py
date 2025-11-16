from django.core.management.base import BaseCommand
from api.models import HomePageContent


class Command(BaseCommand):
    help = 'Initialize home page content with default values'

    def handle(self, *args, **kwargs):
        try:
            # Get or create the home page content
            content, created = HomePageContent.objects.get_or_create(id=1)

            if created:
                self.stdout.write(self.style.SUCCESS('✓ Home page content created with default values'))
            else:
                self.stdout.write(self.style.WARNING('⚠ Home page content already exists'))

            # Display current values
            self.stdout.write('\nCurrent Home Page Content:')
            self.stdout.write(f'\nHero Section:')
            self.stdout.write(f'  Title: {content.hero_title}')
            self.stdout.write(f'  Subtitle: {content.hero_subtitle}')
            self.stdout.write(f'  Background Image: {content.hero_background_image or "Not set"}')
            self.stdout.write(f'  CTA Button: {content.hero_cta_button_text}')

            self.stdout.write(f'\nStatistics:')
            self.stdout.write(f'  Experience: {content.stats_experience_value} - {content.stats_experience_label}')
            self.stdout.write(f'  Projects: {content.stats_projects_value} - {content.stats_projects_label}')
            self.stdout.write(f'  Families: {content.stats_families_value} - {content.stats_families_label}')
            self.stdout.write(f'  Sq.Ft: {content.stats_sqft_value} - {content.stats_sqft_label}')

            self.stdout.write(f'\nFooter Information:')
            self.stdout.write(f'  Address: {content.footer_office_address}')
            self.stdout.write(f'  Phone: {content.footer_phone_number}')
            self.stdout.write(f'  Email: {content.footer_email}')
            self.stdout.write(f'  WhatsApp: {content.footer_whatsapp_number}')

            self.stdout.write(f'\n{self.style.SUCCESS("✓ Home page setup complete!")}')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error setting up home page: {str(e)}'))
