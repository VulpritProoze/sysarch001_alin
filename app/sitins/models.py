from django.db import models
from backend.choices import SITIN_PURPOSE_CHOICES, PROGRAMMING_LANGUAGE_CHOICES, LAB_ROOM_CHOICES, SITIN_STATUS_CHOICES
from django.contrib.auth.models import User

class Sitin(models.Model):
    purpose = models.CharField(max_length=255, choices=SITIN_PURPOSE_CHOICES, blank=True, null=True)
    programming_language = models.CharField(max_length=255, choices=PROGRAMMING_LANGUAGE_CHOICES, blank=True, null=True)
    lab_room = models.CharField(max_length=50, choices=LAB_ROOM_CHOICES, blank=True, null=True)
    sitin_details = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=SITIN_STATUS_CHOICES, default="none") # none, approved, denied
    request_date = models.DateTimeField(null=True, blank=True)
    sitin_date = models.DateTimeField(null=True, blank=True)
    logout_date = models.DateTimeField(null=True, blank=True)
    feedback = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"By {self.user.username}, at {self.lab_room}, status: {self.status}"