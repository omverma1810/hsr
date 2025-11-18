# Generated migration for adding about_our_story_image_url field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_pageheroimages'),
    ]

    operations = [
        migrations.AddField(
            model_name='pageheroimages',
            name='about_our_story_image_url',
            field=models.URLField(blank=True, help_text='URL for About page "Our Story" section image', null=True),
        ),
    ]

