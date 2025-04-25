from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from backend.admin import admin_site

urlpatterns = [
    path('admin/', admin_site.urls),
    path('', include('backend.urls')),
    path('reservations/', include('reservations.urls')),
]

handler404 = 'backend.views.error_404_view'

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls))
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)