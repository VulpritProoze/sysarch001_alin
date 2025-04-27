from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    path('', views.reservation, name='reservations-index'),
    path('create/', views.SitinRequestCreateView.as_view(), name='reservations-create'),
]