from django.db import models

class Notification(models.Model):
    notification_type = models.CharField(max_length=50, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
