from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import CustomLoginView, CustomLogoutView, ProfileUpdateView, AnnouncementCommentView

urlpatterns = [
    # path('', auth_views.LoginView.as_view(template_name='backend/pages/login.html'), name='login'),
    path('', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
    path('home/', views.home, name='user-home'), 
    path('profile/', views.profile, name='user-profile'),
    path('profile/<int:idno>', ProfileUpdateView.as_view(), name='user-profile-update'),
    path('announcements/', views.announcements, name='user-announcements'),
    path('announcements/comments/', AnnouncementCommentView.as_view(), name='user-announcementcomment'),
    path('reservation/', views.reservation, name='user-reservation'),
    path('sitin_history/', views.sitin_history, name='user-sitin_history'),
    path('sessions/', views.sessions, name='user-sessions'),
]
