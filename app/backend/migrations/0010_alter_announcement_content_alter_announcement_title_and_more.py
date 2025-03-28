# Generated by Django 5.1.6 on 2025-02-24 05:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0009_announcementcomment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='announcement',
            name='content',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='announcement',
            name='title',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='announcementcomment',
            name='comment',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='course',
            field=models.CharField(blank=True, max_length=80, null=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='email',
            field=models.EmailField(blank=True, max_length=80, null=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='firstname',
            field=models.CharField(blank=True, max_length=80, null=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='lastname',
            field=models.CharField(blank=True, max_length=80, null=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='level',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='middlename',
            field=models.CharField(blank=True, max_length=80, null=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='sessions',
            field=models.IntegerField(blank=True, default=30, null=True),
        ),
    ]
