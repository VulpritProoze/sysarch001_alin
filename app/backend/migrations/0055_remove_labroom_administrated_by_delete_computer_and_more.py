# Generated by Django 5.1.6 on 2025-04-25 02:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0054_alter_labresource_created_by_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='labroom',
            name='administrated_by',
        ),
        migrations.DeleteModel(
            name='Computer',
        ),
        migrations.DeleteModel(
            name='LabRoom',
        ),
    ]
