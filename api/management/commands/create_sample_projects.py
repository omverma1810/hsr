from django.core.management.base import BaseCommand
from api.models import Project, ProjectGalleryImage, ProjectFloorPlan, AdminUser
from django.utils import timezone


class Command(BaseCommand):
    help = 'Create sample projects with complete data for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample projects with complete data...')

        # Get or create admin user
        try:
            admin_user = AdminUser.objects.filter(is_superuser=True).first()
        except:
            admin_user = None

        # Sample projects data
        projects_data = [
            {
                'title': 'Green Valley Phase 2',
                'location': 'Karimnagar, Telangana',
                'rera_number': 'P02400004567',
                'description': '''Green Valley Phase 2 offers premium 2BHK and 3BHK apartments with world-class amenities.
Located in the heart of Karimnagar, this project features modern architecture, spacious layouts, and eco-friendly design.
Perfect for families looking for a luxurious yet affordable living experience.''',
                'status': 'upcoming',
                'is_featured': True,
                'hero_image_url': 'https://readdy.ai/api/search-image?query=modern%20residential%20apartment%20complex%20with%20greenery&width=1200&height=600&seed=1&orientation=landscape',
                'configurations': {
                    '2bhk': True,
                    '3bhk': True,
                },
                'amenities': {
                    'swimming_pool': True,
                    'childrens_play_area': True,
                    'gym': True,
                    'clubhouse': True,
                    'security': True,
                    'parking': True,
                    'garden': True,
                },
            },
            {
                'title': 'Emerald Heights',
                'location': 'Karimnagar, Telangana',
                'rera_number': 'P02400004568',
                'description': '''Emerald Heights brings luxury living to Karimnagar with spacious 3BHK apartments.
This ongoing project features state-of-the-art amenities including a rooftop infinity pool, modern gym,
and landscaped gardens. Experience elevated living at its finest.''',
                'status': 'ongoing',
                'is_featured': False,
                'hero_image_url': 'https://readdy.ai/api/search-image?query=luxury%20high%20rise%20residential%20building&width=1200&height=600&seed=2&orientation=landscape',
                'configurations': {
                    '3bhk': True,
                    '4bhk': True,
                },
                'amenities': {
                    'swimming_pool': True,
                    'childrens_play_area': True,
                    'gym': True,
                    'clubhouse': True,
                    'security': True,
                    'parking': True,
                    'jogging_track': True,
                    'power_backup': True,
                },
            },
            {
                'title': 'Garden View Apartments',
                'location': 'Karimnagar, Telangana',
                'rera_number': 'P02400004569',
                'description': '''Garden View Apartments is a completed project offering affordable 1BHK and 2BHK homes.
With 100+ happy families already residing here, this community offers peaceful living with essential amenities
and excellent connectivity to schools, hospitals, and shopping centers.''',
                'status': 'completed',
                'is_featured': True,
                'hero_image_url': 'https://readdy.ai/api/search-image?query=residential%20garden%20apartments%20community&width=1200&height=600&seed=3&orientation=landscape',
                'configurations': {
                    '1bhk': True,
                    '2bhk': True,
                },
                'amenities': {
                    'childrens_play_area': True,
                    'security': True,
                    'parking': True,
                    'garden': True,
                    'power_backup': True,
                },
            },
            {
                'title': 'Royal Villas',
                'location': 'Karimnagar, Telangana',
                'rera_number': 'P02400004570',
                'description': '''Royal Villas presents exclusive independent villas with private gardens and premium finishes.
Each villa is designed for spacious family living with 4BHK configurations, private parking, and modern amenities.
A gated community offering the perfect blend of privacy and community living.''',
                'status': 'upcoming',
                'is_featured': True,
                'hero_image_url': 'https://readdy.ai/api/search-image?query=luxury%20villa%20residential%20community&width=1200&height=600&seed=4&orientation=landscape',
                'configurations': {
                    'villa': True,
                    '4bhk': True,
                },
                'amenities': {
                    'swimming_pool': True,
                    'clubhouse': True,
                    'security': True,
                    'parking': True,
                    'garden': True,
                    'community_hall': True,
                },
            },
            {
                'title': 'Sunshine Duplex Homes',
                'location': 'Karimnagar, Telangana',
                'rera_number': 'P02400004571',
                'description': '''Sunshine Duplex Homes offers modern duplex residences with contemporary design.
Featuring spacious layouts across two floors, these homes are perfect for growing families.
Includes dedicated parking, terraces, and premium fixtures throughout.''',
                'status': 'ongoing',
                'is_featured': False,
                'hero_image_url': 'https://readdy.ai/api/search-image?query=modern%20duplex%20homes%20residential&width=1200&height=600&seed=5&orientation=landscape',
                'configurations': {
                    'duplex': True,
                    '3bhk': True,
                },
                'amenities': {
                    'security': True,
                    'parking': True,
                    'garden': True,
                    'power_backup': True,
                },
            },
        ]

        created_projects = []
        for project_data in projects_data:
            project, created = Project.objects.get_or_create(
                rera_number=project_data['rera_number'],
                defaults={
                    **project_data,
                    'created_by': admin_user,
                    'updated_by': admin_user,
                }
            )

            if created:
                created_projects.append(project)
                self.stdout.write(self.style.SUCCESS(f'✅ Created project: {project.title}'))

                # Add sample gallery images
                gallery_images = [
                    {
                        'image_url': f'https://readdy.ai/api/search-image?query={project.title.replace(" ", "%20")}%20exterior&width=800&height=600&seed={project.id * 10 + 1}',
                        'caption': 'Exterior View',
                        'display_order': 1,
                    },
                    {
                        'image_url': f'https://readdy.ai/api/search-image?query={project.title.replace(" ", "%20")}%20lobby&width=800&height=600&seed={project.id * 10 + 2}',
                        'caption': 'Lobby Area',
                        'display_order': 2,
                    },
                    {
                        'image_url': f'https://readdy.ai/api/search-image?query={project.title.replace(" ", "%20")}%20amenities&width=800&height=600&seed={project.id * 10 + 3}',
                        'caption': 'Amenities',
                        'display_order': 3,
                    },
                ]

                for img_data in gallery_images:
                    ProjectGalleryImage.objects.create(
                        project=project,
                        **img_data
                    )

                self.stdout.write(self.style.SUCCESS(f'   ✅ Added {len(gallery_images)} gallery images'))

                # Add sample floor plans
                configs = project.get_configurations_list()
                for i, config in enumerate(configs[:2], 1):  # Add up to 2 floor plans
                    ProjectFloorPlan.objects.create(
                        project=project,
                        title=f'{config.upper()} Floor Plan',
                        file_url=f'https://readdy.ai/api/search-image?query={config}%20floor%20plan%20architectural&width=800&height=1000&seed={project.id * 100 + i}',
                        display_order=i,
                    )

                self.stdout.write(self.style.SUCCESS(f'   ✅ Added {len(configs[:2])} floor plans'))

        self.stdout.write(self.style.SUCCESS(f'\n✅ Created {len(created_projects)} sample projects with complete data!'))
        self.stdout.write(self.style.SUCCESS('   Projects include: hero images, gallery images, floor plans, configurations, and amenities.'))
