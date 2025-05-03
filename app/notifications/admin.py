from django.contrib import admin
from backend.admin import admin_site
from .models import Notification

class NotificationsAdmin(admin.ModelAdmin):
    list_display = ('id', 'badge_type', 'message', 'url', 'timestamp', 'is_read', 'user')

    def has_add_permission(self, request, obj=None):
        return False

admin_site.register(Notification, NotificationsAdmin)
