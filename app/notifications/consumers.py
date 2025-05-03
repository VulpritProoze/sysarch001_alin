import json
from datetime import datetime
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Notification

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)
    
class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.scope['user'].is_authenticated:
            await self.close()
            return

        self.user = self.scope['user']
        self.group_name = f'user_{self.user.id}'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial notifications and unread count
        await self.send_initial_data()
        
    # load initial_data. Client will filter if notification_type = 'initial_data', then it
    # have a different behavior of displaying the notifications
    async def send_initial_data(self):
        notifications = await sync_to_async(list)(
            Notification.objects.filter(user=self.user)
                .order_by('-timestamp')[:10]
                .values('id', 'badge_type', 'message', 'url', 'timestamp', 'is_read')
        )
        
        # Convert datetime objects to ISO format strings
        serialized_notifications = []
        for notification in notifications:
            notification = dict(notification)  # Convert QuerySet dict to regular dict
            notification['timestamp'] = notification['timestamp'].isoformat()
            serialized_notifications.append(notification)
            
        unread_count = await sync_to_async(Notification.objects.filter(
            user=self.user, 
            is_read=False
        ).count)()
        
        await self.send(text_data=json.dumps({
            'notification_type': 'initial_data',
            'notifications': serialized_notifications,
            'unread_count': unread_count
        }))
    
    # Logic that handles sneding notification to client in json format
    async def notification_message(self, event):
        try:
            await self.send(text_data=json.dumps(event, cls=DateTimeEncoder))
        except Exception as e:
            print(f"Error sending notification: {e}")
    
    # Logic that handles incoming websocket messages. If type is 'mark_read' then the notification
    # will be marked as read in database
    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('type') == 'mark_read':
            await self.mark_notification_read(data['id'])
            
    @sync_to_async
    def mark_notification_read(self, notification_id):
        Notification.objects.filter(
            id=notification_id,
            user=self.user
        ).update(is_read=True)
        # Send updated unread count
        unread_count = Notification.objects.filter(
            user=self.user, 
            is_read=False
        ).count()
        self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'notification.message',
                'notification_type': 'unread_count',
                'unread_count': unread_count
            }
        )