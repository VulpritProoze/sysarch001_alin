import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Notification

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("Scope user:", self.scope['user'])  # Debug line
        print("Auth:", self.scope['user'].is_authenticated)  # Debug line
        
        # Reject connection if not authenticated
        if not self.scope['user'].is_authenticated:
            print("Rejecting connection - user not authenticated")
            await self.close()
            return

        self.user = self.scope['user']
        self.group_name = f'user_{self.user.id}'

        # Join user's personal group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial unread notifs
        await self.send_unread_notifications()
        
    async def disconnect(self, close_code):
        # Leave group if auth
        if hasattr(self, 'group_name') and self.scope['user'].is_authenticated:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
            
    async def send_unread_notifications(self):
        notifications = await sync_to_async(list)(
            Notification.objects.filter(user=self.user, is_read=False)
                .order_by('timestamp')[:10]
                .values('id', 'message', 'url', 'timestamp')
        )
        
        for notification in notifications:
            await self.send(text_date=json.dumps({
                'notification_type': 'notification',
                'id': notification['id'],
                'message': notification['message'],
                'url': notification['url'],
                'is_read': False
            }))
            
    async def notification_message(self, event):
        # Send notifs to websocket
        await self.send(text_date=json.dumps(event))