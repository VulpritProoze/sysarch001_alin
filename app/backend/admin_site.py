from django.urls import path
from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.core.paginator import Paginator
from sitins.models import Sitin
from django.contrib.admin import AdminSite
from sitins import views
from .models import Announcement
from .choices import SITIN_PURPOSE_CHOICES, LAB_ROOM_CHOICES, LEVEL_CHOICES

class CustomAdminSite(AdminSite):
    index_template = 'admin/custom_index.html'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("sitins/finishedsitins/export_all_sitins/", self.admin_view(self.export_all_sitins), name="admin-export_all_sitins"),
            path("sitins/finishedsitins/export_all_sitins/<str:file_type>/", views.export_sitins, name="admin-export_sitins_by_type"),
            path('auth/', self.admin_view(self.auth_view), name="admin-auth_index"),
            path('backend/', self.admin_view(self.backend_view), name="admin-backend_index"),
            path('sitins/', self.admin_view(self.sitin_view), name="admin-sitin_index"),
            path('reservations/', self.admin_view(self.reservations_view), name="admin-reservations_index"),
            path('notifications/', self.admin_view(self.notifications_view), name="admin-notifications_index"),
        ]
        return custom_urls + urls

    def auth_view(self, request):
        context = self.each_context(request)
        auth_app = [app for app in self.get_app_list(request) if app['app_label'] == 'auth']
        context.update({
            'app_label': 'auth',   
            'title': 'Authorization Management',
            'app_list': auth_app,
        })
        return render(request, "admin/auth/auth_index.html", context)
    
    def backend_view(self, request):
        context = self.each_context(request)
        backend_app = [app for app in self.get_app_list(request) if app['app_label'] == 'backend']
        context.update({
            'app_label': 'backend',   
            'title': 'General Management',
            'app_list': backend_app,
        })
        return render(request, "admin/backend/backend_index.html", context)

    def sitin_view(self, request):
        context = self.each_context(request)
        sitin_app = [app for app in self.get_app_list(request) if app['app_label'] == 'sitins']
        programming_language_stats = Sitin.objects.values("programming_language").annotate(count=Count("programming_language"))
        purpose_stats = Sitin.objects.values("purpose").annotate(count=Count("purpose"))
        lab_room_stats = Sitin.objects.values("lab_room").annotate(count=Count("lab_room"))
        context.update({
            'app_label': 'sitins',
            'title': 'Sitins',
            'app_list': sitin_app,
        })
        context["programming_language_stats"] = programming_language_stats
        context["purpose_stats"] = purpose_stats
        context["lab_room_stats"] = lab_room_stats 
           
        # Add sitins to the context
        users = User.objects.prefetch_related(
            'registration'
        ).values(
            'id',
            'registration__idno',
            'registration__firstname',
            'registration__middlename',
            'registration__lastname',
            'registration__course',
            'registration__level',
            'registration__sessions',
            'registration__points',
            'registration__sitins_count',
        ).order_by('-registration__points') # Ordered by points by default
        # Fetch filtering for leaderboards
        is_top_performing = request.GET.get('is_top_performing')
        active_tab = 'top_performing'
        if is_top_performing == 'False':
            users = users.order_by('-registration__sitins_count')
            active_tab = 'most_active'
        else:
            print('some kinda problem in the html?')
            
        # Pagination on leaderboard
        paginator = Paginator(users, 25)
        page_number = request.GET.get('page')   
        page_obj = paginator.get_page(page_number)
        
        # Pass as context
        context['users'] = page_obj
        context['active_tab'] = active_tab
        return render(request, "admin/sitin/sitin_index.html", context)

    def reservations_view(self,request):
        context = self.each_context(request)
        reservations_app = [app for app in self.get_app_list(request) if app['app_label'] == 'reservations']
        context.update({
            'app_label': 'reservations',
            'title': ' Reservations',
            'app_list': reservations_app,
        })
        return render(request, "admin/reservations/reservation_index.html", context)

    def notifications_view(self, request):
        context = self.each_context(request)
        notifications_app = [app for app in self.get_app_list(request) if app['app_label'] == 'notifications']
        context.update({
            'app_label': 'notifications',
            'title': ' Notifications',
            'app_list': notifications_app,
        })
        return render(request, "admin/notifications/notification_index.html", context)
    
    def export_all_sitins(self, request):
        context = self.each_context(request)
        context['app_list'] = self.get_app_list(request)
        context['lab_room_choices'] = LAB_ROOM_CHOICES
        context['purpose_choices'] = SITIN_PURPOSE_CHOICES
        context['level_choices'] = LEVEL_CHOICES
        context['title'] = 'Export Sitins'
        context['filters'] = request.GET
        
        # Sitins context for table display
        # Join tables for more efficient query
        sitins = Sitin.objects.select_related(
            'user',
            'user__registration'
        ).values(
            'user__registration__idno',
            'user__registration__firstname',
            'user__registration__middlename',
            'user__registration__lastname',
            'purpose',
            'lab_room',
            'status',
            'user__registration__sessions',
            'sitin_date',
            'logout_date',
        ).filter(status='finished').order_by('-logout_date')
        
        # Filtering based on filters. Convert to their proper data type, return None if 'None'
        lab_room = request.GET.get('lab_room') if request.GET.get('lab_room') !=  'None' else None
        purpose = request.GET.get('purpose') if request.GET.get('purpose') != 'None' else None
        level = request.GET.get('level') if request.GET.get('level') != 'None' else None
        
        print(lab_room, purpose, level)
        
        if lab_room:
            sitins = sitins.filter(lab_room=lab_room)
        if purpose:
            sitins = sitins.filter(purpose=purpose)
        if level:
            level = int(level)
            sitins = sitins.filter(user__registration__level=level)
            
        paginator = Paginator(sitins, 25)
        page_number = request.GET.get('page')   
        page_obj = paginator.get_page(page_number)
        context['sitins'] = page_obj
        return render(request, "admin/backend/sitin/reports_change_list.html", context)
    
    def index(self, request, extra_context=None):
        # Custom logic for the index page
        total_users = User.objects.count()
        total_announcements = Announcement.objects.count()
        total_sitins = Sitin.objects.count()

        # Prepare extra context to pass to the template
        extra_context = extra_context or {}
        extra_context.update({
            'total_users': total_users,
            'total_announcements': total_announcements,
            'total_sitins': total_sitins,
        })

        # Return the custom index page with the updated context
        return super().index(request, extra_context=extra_context)