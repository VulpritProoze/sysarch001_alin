from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Registration

@receiver(post_save, sender=User)
def create_superuser_registration(sender, instance, created, **kwargs):
    if created and instance.is_superuser:
        Registration.objects.create(username=instance, email=instance.email)