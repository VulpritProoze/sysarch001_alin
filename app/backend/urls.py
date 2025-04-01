from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # path('', auth_views.LoginView.as_view(template_name='backend/pages/login.html'), name='login'),
    path('', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
    path('home/', views.home, name='user-home'), 
    path('profile/', views.profile, name='user-profile'),
    path('profile/<int:idno>/', views.ProfileUpdateView.as_view(), name='user-profile-update'),
    path('announcements/', views.announcements, name='user-announcements'),
    path('announcements/<int:announcement_id>/', views.announcement, name='user-announcement'),
    path('announcements/<int:announcement_id>/comments/', views.AnnouncementCommentCreateView.as_view(), name='user-announcementcomment-create'),
    path('announcements/<int:announcement_id>/comments/<int:pk>/', views.AnnouncementCommentUpdateDeleteView.as_view(), name="user-announcementcomment-updatedelete"),
    path('reservation/', views.reservation, name='user-reservation'),
    # path('sitin/', views.SitinHybridView.as_view(), name='user-sitin'),
    # path('sitin/<int:pk>/', views.SitinDeleteView.as_view(), name='user-sitin-delete'),
    path('sitin_history/', views.sitin_history, name='user-sitin_history'),
    path('sitin_history/<int:pk>/', views.SitinHistoryUpdateView.as_view(), name='user-sitin_history_feedback'),
    path('survey/', views.survey, name='user-survey'),
    path('survey/<int:pk>/', views.SitinSurveyUpdateView.as_view(), name='user-survey-update'),
    path('resources/', views.resources, name='user-resources'),
    path('sessions/', views.sessions, name='user-sessions'),
] 
