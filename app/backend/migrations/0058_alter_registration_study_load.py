# Generated by Django 5.1.6 on 2025-04-27 04:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0057_remove_sitin_user_delete_allsitins_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registration',
            name='study_load',
            field=models.ImageField(blank=True, null=True, upload_to='schedules/'),
        ),
    ]
