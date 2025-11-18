# Generated migration for UploadedImage model

import api.models
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0005_contactsettings_systemstatus_auto_backup_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="UploadedImage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "title",
                    models.CharField(
                        blank=True,
                        help_text="Optional title/name for the image",
                        max_length=255,
                        null=True,
                    ),
                ),
                (
                    "image_file",
                    models.ImageField(
                        help_text="Uploaded image file",
                        upload_to=api.models.uploaded_image_path,
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                ["jpg", "jpeg", "png", "webp", "gif"]
                            )
                        ],
                    ),
                ),
                (
                    "image_url",
                    models.URLField(
                        blank=True,
                        help_text="Public URL for the image (auto-generated)",
                        null=True,
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="Optional description for the image",
                        null=True,
                    ),
                ),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        blank=True,
                        help_text="Admin user who uploaded this image",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="uploaded_images",
                        to="api.adminuser",
                    ),
                ),
            ],
            options={
                "verbose_name": "Uploaded Image",
                "verbose_name_plural": "Uploaded Images",
                "db_table": "uploaded_images",
                "ordering": ["-created_at"],
            },
        ),
    ]
