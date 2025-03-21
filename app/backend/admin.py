from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.decorators import login_required
from django.contrib.admin import AdminSite
from django.forms import BaseInlineFormSet
from django.utils.translation import gettext_lazy as _
from django.urls import path
from django.shortcuts import render
from django.db.models import Count
from . import views
from .models import Registration, Announcement, AnnouncementComment, Sitin
from .choices import LAB_ROOM_CHOICES

class CustomAdminSite(AdminSite):
    index_template = 'admin/custom_index.html'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('approve-sitin/', views.approve_sitin, name='admin-approve-sitin'),
            path('logout-sitin/', views.logout_sitin, name='admin-logout-sitin'),
            path("backend/finishedsitins/export_all_sitins/", self.admin_view(self.export_all_sitins), name="admin-export_all_sitins"),
            path("backend/finishedsitins/export_all_sitins/<str:lab_room>/<str:file_type>/", views.export_sitins, name="admin-export_sitins_by_type"),
            path('auth/', self.admin_view(self.auth_view), name="admin-auth_index"),
            path('backend/', self.admin_view(self.backend_view), name="admin-backend_index"),
            path('sitin/', self.admin_view(self.sitin_view), name="admin-sitin_index"),
            # custom ahh urls for app_list models
            path('sitin/currentsitins/', self.admin_view(CurrentSitinsAdmin(CurrentSitins, self).changelist_view), name='current_sitins_changelist'),
            path('sitin/finishedsitins/', self.admin_view(FinishedSitinsAdmin(FinishedSitins, self).changelist_view), name='finished_sitins_changelist'),
            path('sitin/extrasitins/', self.admin_view(ExtraSitinsAdmin(ExtraSitins, self).changelist_view), name='extra_sitins_changelist'),
            path('sitin/sitins/', self.admin_view(CustomSitinsAdmin(Sitin, self).changelist_view), name='sitins_changelist'),
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
        sitin_app = [app for app in self.get_app_list(request) if app['app_label'] == 'custom_sitins']
        programming_language_stats = Sitin.objects.values("programming_language").annotate(count=Count("programming_language"))
        purpose_stats = Sitin.objects.values("purpose").annotate(count=Count("purpose"))
        lab_room_stats = Sitin.objects.values("lab_room").annotate(count=Count("lab_room"))
        context.update({
            'app_label': 'custom_sitins',
            'title': 'Sitin Management',
            'app_list': sitin_app,
        })
        context["programming_language_stats"] = programming_language_stats
        context["purpose_stats"] = purpose_stats
        context["lab_room_stats"] = lab_room_stats
        return render(request, "admin/sitin/sitin_index.html", context)
    
    def export_all_sitins(self, request):
        context = self.each_context(request)
        context['app_list'] = self.get_app_list(request)
        context['lab_room_choices'] = LAB_ROOM_CHOICES
        context['title'] = 'Export Sitins'
        return render(request, "admin/backend/sitin/reports_change_list.html", context)
    
    def get_app_list(self, request):
        original_app_list = super().get_app_list(request)
        custom_apps = {
            "Authentication and Authorization": {
                "app_label": "auth",
                "app_url": "/admin/auth/",
                "name": "Authentication and Authorization",
                "models": []
            },
            "General Management": {
                "app_label": "backend",
                "app_url": "/admin/backend/",
                "name": "General Management",
                "models": []
            },
            "Sit-in Management": {
                "app_label": "custom_sitins",
                "app_url": "/admin/sitin/",
                "name": "Sit-in Management",
                "models" : []
            },
            # "Other Models": {
            #     "app_label": "custom_other_models",
            #     "models": []
            # }
        }
        auth_models = ["User", "Registration"]
        general_models = ["Announcement", "AnnouncementComment"]
        sitin_models = ["Sitin", "SitinRequests", "CurrentSitins", "FinishedSitins", "ExtraSitins"]

        for app in original_app_list:
            for model in app["models"]:
                model_name = model["object_name"]
                if model_name in auth_models:
                    custom_apps["Authentication and Authorization"]["models"].append(model)
                elif model_name in general_models:
                    custom_apps["General Management"]["models"].append(model)
                elif model_name in sitin_models:
                    # have to add this cuz i had to customize urls
                    if model_name == "Sitin":
                        model["admin_url"] = "/admin/sitin/sitins/"
                    elif model_name == "CurrentSitins":
                        model["admin_url"] = "/admin/sitin/currentsitins/"
                    elif model_name == "FinishedSitins":
                        model["admin_url"] = "/admin/sitin/finishedsitins/"
                    elif model_name == "ExtraSitins":
                        model["admin_url"] = "/admin/sitin/extrasitins/"
                    custom_apps["Sit-in Management"]["models"].append(model)
        desired_order = ['Sitin', 'SitinRequests', 'CurrentSitins', 'FinishedSitins', "ExtraSitins"]
        custom_apps["Sit-in Management"]['models'].sort(key=lambda x: desired_order.index(x['object_name']) if x['object_name'] in desired_order else len(desired_order))
                # else:
                #     custom_apps["Other Models"]["models"].append(model)
        return list(custom_apps.values())
    
    def index(self, request, extra_context=None):
        # Custom logic for the index page
        total_users = User.objects.count()
        total_announcements = Announcement.objects.count()
        total_comments = AnnouncementComment.objects.count()
        total_sitins = Sitin.objects.count()

        # Add more statistics or custom data
        recent_announcements = Announcement.objects.all().order_by('-date')[:5]
        recent_sitins = Sitin.objects.all().order_by('-date')[:5]

        # Prepare extra context to pass to the template
        extra_context = extra_context or {}
        extra_context.update({
            'total_users': total_users,
            'total_announcements': total_announcements,
            'total_comments': total_comments,
            'total_sitins': total_sitins,
            'recent_announcements': recent_announcements,
            'recent_sitins': recent_sitins,
        })

        # Return the custom index page with the updated context
        return super().index(request, extra_context=extra_context)
    
# Instantiate your custom admin site
admin_site = CustomAdminSite(name='custom_admin')

admin_site.site_header = "CCS Sitin Administration"
admin_site.site_title = "CCS Sitin Administration"
admin_site.index_title = "Welcome to the Sitin Administration Panel of CCS Department"

# @admin.register(Registration, site=admin_site)
class RegistrationInline(admin.StackedInline):
    model = Registration 
    # list_display = ('idno', 'username', 'firstname', 'lastname', 'middlename', 'course', 'level', 'email', 'sessions')
    # search_fields = ('firstname', 'middlename', 'lastname', 'username__username')
    # list_filter = ('course', 'level')
    
    # Change the verbose name directly in the model's _meta
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        self.model._meta.verbose_name = "User Detail"
        self.model._meta.verbose_name_plural = "User Details"
        return qs

# @admin.site.unregister(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff')
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ('Personal info', {'fields': ('email',)}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    inlines = UserAdmin.inlines + (RegistrationInline,)

admin_site.register(User, CustomUserAdmin)
    
class SuperuserFilter(admin.SimpleListFilter):
    title = "Admin"
    parameter_name = "superuser"

    def lookups(self, request, model_admin):
        superusers = User.objects.filter(is_superuser=True)
        return [(user.id, user.username) for user in superusers]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(superuser__id=self.value())
        return queryset
    
# @admin.register(Announcement, site=admin_site)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'date', 'superuser')
    list_display_links = ('title',)
    search_fields = ('superuser__username', 'superuser__registration__firstname', 'superuser__registration__middlename','superuser__registration__lastname',)
    list_filter = ('date', 'updated_at', SuperuserFilter)
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.superuser = request.user 
        super().save_model(request, obj, form, change)
        
# @admin.register(AnnouncementComment, site=admin_site)
# class AnnouncementCommentAdmin(admin.ModelAdmin):
#     list_display = ('comment', 'date', 'announcement', 'user')
#     list_display_links = ('comment',)
#     search_fields = ('user__username', 'user__username', 'user__registration__firstname', 'user__registration__middlename','user__registration__lastname',)
#     list_filter = ( 'announcement', 'date', 'updated_at',)

#     # Change the verbose name directly in the model's _meta
#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         self.model._meta.verbose_name = "Announcement Comment"
#         self.model._meta.verbose_name_plural = "Announcement Comments"
#         return qs

# Put a default value to user field para ma save frfr
# class AnnouncementCommentFormSet(BaseInlineFormSet):
#     def save_new(self, form, commit=True):
#         form.instance.user = self.request.user  # Set the user field
#         return super().save_new(form, commit=commit)
    
class AnnouncementCommentInline(admin.TabularInline):
    model = AnnouncementComment 
    fields = ('user', 'comment', 'date', 'updated_at')
    readonly_fields = ('date', 'updated_at',)
    extra = 0

class ExtendedAnnouncementAdmin(AnnouncementAdmin):
    inlines = (AnnouncementCommentInline,)

admin_site.register(Announcement, ExtendedAnnouncementAdmin)

class BaseSitinAdmin(admin.ModelAdmin):
    list_display = ("get_user_idno", "get_fullname", "purpose", "lab_room", "status", "user__registration__sessions", "get_formatted_date", "get_formatted_logout_date")
    search_fields = ("user__registration__idno", "user__username", "user__registration__firstname", 
                     "user__registration__middlename", "user__registration__lastname")
    list_filter = ("programming_language", "purpose", "lab_room", "status", "date")
    change_list_template = 'admin/custom_change_list.html'
    
    def get_user_idno(self, obj):
        return obj.user.registration.idno if hasattr(obj.user, "registration") else None

    get_user_idno.short_description = "Student ID"
    get_user_idno.admin_order_field = "user__registration__idno"

    def get_fullname(self, obj):
        if hasattr(obj.user, "registration"):
            reg = obj.user.registration
            return f"{reg.firstname} {reg.middlename} {reg.lastname}"
        return None
    get_fullname.short_description = "Fullname"
    get_fullname.admin_order_field = 'user__registration__lastname'

    def get_formatted_date(self, obj):
        return obj.date  # You can format the date here if needed

    get_formatted_date.short_description = "Request Date"  # Change the display name here
    get_formatted_date.admin_order_field = "date"  # Ensure the field is sortable by date

    def get_formatted_logout_date(self, obj):
        return obj.logout_date  # You can format the date here if needed

    get_formatted_logout_date.short_description = "Time-out"  # Change the display name here
    get_formatted_logout_date.admin_order_field = "logout_date"  # Ensure the field is sortable by date

    def get_formatted_sitin_date(self, obj):
        return obj.sitin_date  # You can format the date here if needed

    get_formatted_sitin_date.short_description = "Time-in"  # Change the display name here
    get_formatted_sitin_date.admin_order_field = "sitin_date"  # Ensure the field is sortable by date
    
class ExtraSitinsAdmin(BaseSitinAdmin):
    list_display = ("get_user_idno", "get_fullname", "purpose", "lab_room", "status", "user__registration__sessions", 'get_formatted_date', "get_formatted_sitin_date", "get_formatted_logout_date", 'feedback')
    list_editable = ('status',)
    
    class Meta:
        verbose_name = "All Sitin"
        verbose_name_plural = "All Sitins"  # Plural version

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        self.model._meta.verbose_name = "All Sitin"
        self.model._meta.verbose_name = "All Sitins"
        return qs

class CustomSitinsAdmin(BaseSitinAdmin):
    change_list_template = 'admin/backend/sitin/searchsitins_change_list.html'
    search_fields = ('user__registration__idno',)
    # change_list_template = 'admin/custom_change_list.html'

    def get_model_perms(self, request):
        return {"view": True}  # Hide "Add" and "Delete" buttons
    
    def has_add_permission(self, request):
        return False
        
    # Change the verbose name directly in the model's _meta
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        self.model._meta.verbose_name = "Search Sitin"
        self.model._meta.verbose_name_plural = "Search Sitins"
        return qs
    
    def changelist_view(self, request, extra_context=None):
        # Aggregate statistics
        pending_sitins = Sitin.objects.filter(status="pending")
        current_sitins = Sitin.objects.filter(status="approved")
        finished_sitins = Sitin.objects.filter(status="finished")
        # Pass stats to the template
        extra_context = extra_context or {}
        extra_context["title"] = _("Select Students to Approve Sit-ins")
        extra_context["pending_sitins"] = pending_sitins
        extra_context["current_sitins"] = current_sitins
        extra_context["finished_sitins"] = finished_sitins

        return super().changelist_view(request, extra_context=extra_context)

class SitinRequestsAdmin(BaseSitinAdmin):  
    def get_queryset(self, request):
        return super().get_queryset(request).filter(status="pending")

    def get_model_perms(self, request):
        return {"view": True}  # Hide "Add" and "Delete" buttons

    def has_add_permission(self, request):
        return False

class CurrentSitinsAdmin(BaseSitinAdmin):
    change_list_template = 'admin/backend/sitin/logout_change_list.html'
    
    def get_queryset(self, request):
        return super().get_queryset(request).filter(status="approved")

    def get_model_perms(self, request):
        return {"view": True}  # Hide "Add" and "Delete" buttons
    
    def has_add_permission(self, request):
        return False

    # Fuckign stupid ass methof    
    # def save_model(self, request, obj, form, change):
    #     """Reduce sessions by 1 when status is changed to 'finished'"""
    #     if obj.status == "finished" and obj.user.registration:
    #         regis = obj.user.registration
    #         regis.logout_date = now()
    #         if regis.sessions > 0:
    #             regis.sessions -= 1
    #         regis.save()
    #     super().save_model(request, obj, form, change)
    
class FinishedSitinsAdmin(BaseSitinAdmin):    
    list_display = ("get_user_idno", "get_fullname", "purpose", "lab_room", "status", "user__registration__sessions", "get_formatted_logout_date", "feedback")
    change_list_template = "admin/backend/sitin/timedout_change_list.html"

    def get_model_perms(self, request):
        return {"view": True}  # Hide "Add" and "Delete" buttons
    
    def has_add_permission(self, request):
        return False
      
    def get_queryset(self, request):
        qs = super().get_queryset(request).filter(status="finished")
        self.model._meta.verbose_name = "View Sit-in History"
        self.model._meta.verbose_name_plural = "View Sit-in History"
        return qs
    
    def get_readonly_fields(self, request, obj=None):
        """Make the feedback field uneditable in the change form."""
        return super().get_readonly_fields(request, obj) + ("feedback",)

# Proxy models
class ExtraSitins(Sitin):
    class Meta:
        proxy = True
        verbose_name = "All Sitin"
        verbose_name_plural = "All Sitins"  # Plural version

class SitinRequests(Sitin):
    class Meta:
        proxy = True
        verbose_name = "Pending Sit-in"
        verbose_name_plural = "Pending Sit-ins"

class CurrentSitins(Sitin):
    class Meta:
        proxy = True
        verbose_name = "Current Sit-in"
        verbose_name_plural = "Current Sit-ins"

class FinishedSitins(Sitin):
    class Meta:
        proxy = True
        verbose_name = "Timed-out Sit-in"
        verbose_name_plural = "Timed-out Sit-ins"

admin_site.register(ExtraSitins, ExtraSitinsAdmin)
admin_site.register(Sitin, CustomSitinsAdmin)
# admin_site.register(SitinRequests, SitinRequestsAdmin)
admin_site.register(CurrentSitins, CurrentSitinsAdmin)
admin_site.register(FinishedSitins, FinishedSitinsAdmin)

    
# admin
# ganymede14337
