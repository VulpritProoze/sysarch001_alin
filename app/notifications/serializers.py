from rest_framework import serializers
from .models import Notification
from django.utils import timezone

class NotificationSerializer(serializers.ModelSerializer):
    timestamp = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'message', 'timestamp', 'url', 'is_read']

    def get_timestamp(self, obj):
        return self.time_ago(obj.timestamp)
    
    def time_ago(self, value):
        if not value:
            return ""
        
        now = timezone.localtime(timezone.now())
        value = timezone.localtime(value)

        diff = now - value

        seconds = diff.total_seconds()
        if seconds < 60:
            return f"{int(seconds)} seconds ago"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        else:
            return value.strftime("%b %d, %Y, %I:%M %p ")  # Fallback to date if > 1 day