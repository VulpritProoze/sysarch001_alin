from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    path('sitin_history/', views.sitin_history, name='sitins-sitin_history'),
    path('sitin_history/<int:pk>/', views.SitinHistoryUpdateView.as_view(), name='sitins-sitin_history_feedback'),
    
]