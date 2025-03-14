# Generated by Django 5.1.6 on 2025-02-27 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0013_announcement_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='registration',
            name='profilepicture',
        ),
        migrations.AddField(
            model_name='registration',
            name='profilepicture_lg',
            field=models.ImageField(blank=True, default='profiles/default_lg.jpg', null=True, upload_to='profiles/'),
        ),
        migrations.AddField(
            model_name='registration',
            name='profilepicture_md',
            field=models.ImageField(blank=True, default='profiles/default_md.jpg', null=True, upload_to='profiles/'),
        ),
        migrations.AddField(
            model_name='registration',
            name='profilepicture_sm',
            field=models.ImageField(blank=True, default='profiles/default_sm.jpg', null=True, upload_to='profiles/'),
        ),
    ]
