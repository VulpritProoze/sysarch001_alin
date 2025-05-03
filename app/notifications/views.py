from django.shortcuts import render
from .models import Notification

def notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'notifications/notifications.html', context={ 'notifications': notifications })