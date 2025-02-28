from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import CustomLoginView, CustomLogoutView, ProfileUpdateView, AnnouncementCommentCreateView, AnnouncementCommentUpdateDeleteView

urlpatterns = [
    # path('', auth_views.LoginView.as_view(template_name='backend/pages/login.html'), name='login'),
    path('', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
    path('home/', views.home, name='user-home'), 
    path('profile/', views.profile, name='user-profile'),
    path('profile/<int:idno>', ProfileUpdateView.as_view(), name='user-profile-update'),
    path('announcements/', views.announcements, name='user-announcements'),
    path('announcements/<int:announcement_id>', views.announcement, name='user-announcement'),
    path('announcements/<int:announcement_id>/comments/', AnnouncementCommentCreateView.as_view(), name='user-announcementcomment-create'),
    path('announcements/<int:announcement_id>/comments/<int:pk>', AnnouncementCommentUpdateDeleteView.as_view(), name="user-announcementcomment-updatedelete"),
    path('reservation/', views.reservation, name='user-reservation'),
    path('sitin/', views.sitin, name='user-sitin'),
    path('sitin_history/', views.sitin_history, name='user-sitin_history'),
    path('sessions/', views.sessions, name='user-sessions'),
]
