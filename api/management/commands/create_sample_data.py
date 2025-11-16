from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import Project, Lead, Testimonial, SystemStatus
import random


class Command(BaseCommand):
    help = 'Create sample data for testing dashboard'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')

        # Create sample projects
        projects_data = [
            {
                'title': 'Green Valley Phase 2',
                'location': 'Karimnagar, Telangana',
                'rera_number': 'P02400004567',
                'description': 'Premium 2BHK and 3BHK apartments with modern amenities',
                'status': 'upcoming',
                'is_featured': True,
            },
            {
                'title': 'Emerald Heights',
                'location': 'Karimnagar, Telangana',
                'rera_number': 'P02400004568',
                'description': 'Luxurious 3BHK apartments with world-class facilities',
                'status': 'ongoing',
                'is_featured': False,
            },
            {
                'title': 'Garden View Apartments',
                'location': 'Karimnagar, Telangana',
                'rera_number': 'P02400004569',
                'description': 'Affordable 2BHK apartments in prime location',
                'status': 'completed',
                'is_featured': True,
            },
        ]

        created_projects = []
        for project_data in projects_data:
            project, created = Project.objects.get_or_create(
                rera_number=project_data['rera_number'],
                defaults=project_data
            )
            created_projects.append(project)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created project: {project.title}'))

        # Create sample leads
        leads_data = [
            {
                'name': 'Rajesh Kumar',
                'email': 'rajesh.kumar@email.com',
                'phone': '+919876543210',
                'message': 'Interested in 2BHK apartment. Please share more details.',
                'status': 'new',
                'source': 'contact_form',
            },
            {
                'name': 'Priya Sharma',
                'email': 'priya.sharma@email.com',
                'phone': '+919876543211',
                'message': 'Looking for 3BHK with good amenities.',
                'status': 'contacted',
                'source': 'whatsapp',
            },
            {
                'name': 'Amit Patel',
                'email': 'amit.patel@email.com',
                'phone': '+919876543212',
                'message': 'Want to schedule a site visit.',
                'status': 'new',
                'source': 'phone_call',
            },
        ]

        for i, lead_data in enumerate(leads_data):
            lead_data['project'] = created_projects[i % len(created_projects)]
            lead, created = Lead.objects.get_or_create(
                email=lead_data['email'],
                defaults=lead_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created lead: {lead.name}'))

        # Create sample testimonials
        testimonials_data = [
            {
                'customer_name': 'Rajesh Kumar',
                'quote': 'HSR Green Homes delivered exactly what they promised. The quality of construction and attention to detail is exceptional.',
                'display_order': 1,
            },
            {
                'customer_name': 'Priya Sharma',
                'quote': 'Moving into Emerald Heights was the best decision we made. The amenities and location are perfect for our family.',
                'display_order': 2,
            },
            {
                'customer_name': 'Amit Patel',
                'quote': 'The team at HSR Green Homes was professional throughout the entire process. Highly recommended!',
                'display_order': 3,
            },
        ]

        for i, testimonial_data in enumerate(testimonials_data):
            testimonial_data['project'] = created_projects[i % len(created_projects)]
            testimonial, created = Testimonial.objects.get_or_create(
                customer_name=testimonial_data['customer_name'],
                project=testimonial_data['project'],
                defaults=testimonial_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created testimonial: {testimonial.customer_name}'))

        # Create/update system status
        system_status = SystemStatus.get_current()
        self.stdout.write(self.style.SUCCESS('System status initialized'))

        self.stdout.write(self.style.SUCCESS('\n✅ Sample data created successfully!'))
