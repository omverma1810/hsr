# Generated manually for PageHeroImages model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_uploadedimage'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageHeroImages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('projects_hero_image_url', models.URLField(blank=True, help_text='URL for Projects page hero background image', null=True)),
                ('about_hero_image_url', models.URLField(blank=True, help_text='URL for About page hero background image', null=True)),
                ('contact_hero_image_url', models.URLField(blank=True, help_text='URL for Contact page hero background image', null=True)),
            ],
            options={
                'verbose_name': 'Page Hero Images',
                'verbose_name_plural': 'Page Hero Images',
                'db_table': 'page_hero_images',
            },
        ),
    ]

