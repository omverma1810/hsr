"""
Management command to setup initial contact settings and system configuration.
Phase 6: Contact Settings & System Configuration
"""

from django.core.management.base import BaseCommand
from api.models import ContactSettings, SystemStatus


class Command(BaseCommand):
    help = 'Setup initial contact settings and system configuration'

    def handle(self, *args, **kwargs):
        self.stdout.write('Setting up contact settings and system configuration...')

        # Create/update contact settings
        contact_settings = ContactSettings.get_current()
        self.stdout.write(self.style.SUCCESS('✅ Contact settings initialized'))

        # Create/update system status
        system_status = SystemStatus.get_current()
        self.stdout.write(self.style.SUCCESS('✅ System status initialized'))

        self.stdout.write(self.style.SUCCESS('\n✅ Contact settings and system configuration setup complete!'))

        # Display current settings
        self.stdout.write('\n📞 Contact Information:')
        self.stdout.write(f'   WhatsApp: {contact_settings.whatsapp_number}')
        self.stdout.write(f'   Phone: {contact_settings.primary_phone}')
        self.stdout.write(f'   Email: {contact_settings.info_email}')
        self.stdout.write(f'   Address: {contact_settings.get_full_address()}')

        self.stdout.write('\n⚙️ System Configuration:')
        self.stdout.write(f'   Site Name: {system_status.site_name}')
        self.stdout.write(f'   Site URL: {system_status.site_url}')
        self.stdout.write(f'   Maintenance Mode: {"Enabled" if system_status.maintenance_mode else "Disabled"}')
        self.stdout.write(f'   Auto Backup: {"Enabled" if system_status.auto_backup_enabled else "Disabled"}')
