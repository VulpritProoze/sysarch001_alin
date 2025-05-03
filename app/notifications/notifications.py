from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification

# Logic that handles centralized creation of notification itself
# Saves notif to database
def send_notification(user, message, url=None, badge_type=None):
    channel_layer = get_channel_layer()
    
    # Create the notif in database
    notification = Notification.objects.create(
        user=user,
        message=message,
        url=url,
        badge_type=badge_type
    )
    
    # Send via websocket
    async_to_sync(channel_layer.group_send)(
        f'user_{user.id}',
        {
            'type': 'notification.message',
            'notification_type': 'notification',
            'id': notification.id,
            'message': notification.message,
            'url': notification.url,
            'badge_type': notification.badge_type,
            'timestamp': notification.timestamp.isoformat(),
            'is_read': False
        }
    )
    
    return notification