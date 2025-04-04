# Generated by Django 5.1.6 on 2025-03-23 03:13

import django.contrib.auth.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('backend', '0033_alter_sitin_status'),
    ]

    operations = [
        migrations.DeleteModel(
            name='SearchSitins',
        ),
        migrations.CreateModel(
            name='UserProxy',
            fields=[
            ],
            options={
                'verbose_name': 'Search Student',
                'verbose_name_plural': 'Search Students',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
