from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification

# Send real-time notif to user
def send_notification(user, message, url=None):
    channel_layer = get_channel_layer()
    
    # Create the notif in database
    notification = Notification.objects.create(
        user=user,
        message=message,
        url=url
    )
    
    # Send via websocket
    async_to_sync(channel_layer.group_send)(
        f'user_{user.id}',
        {
            'notification_type': 'notification.message',
            'id': notification.id,
            'message': notification.message,
            'url': url,
            'timestamp': notification.timestamp.isoformat(),
            'is_read': False
        }
    )
    
    return notification