# Generated by Django 5.1.6 on 2025-02-21 01:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0006_registration_profilepicture'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='profiledescription',
            field=models.TextField(blank=True, null=True),
        ),
    ]
