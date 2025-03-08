from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from django.db.models import Count
from django.db import models
from .models import Registration, Announcement, AnnouncementComment, Sitin

class CustomAdminSite(AdminSite):
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
admin_site.register(User)

admin_site.site_header = "CCS Sitin Administration"
admin_site.site_title = "CCS Sitin Administration"
admin_site.index_title = "Welcome to the Sitin Administration Panel of CCS Department"

@admin.register(Registration, site=admin_site)
class RegistrationAdmin(admin.ModelAdmin):
    class Meta:
        verbose_name_plural = "Users"
    
    list_display = ('idno', 'username', 'firstname', 'lastname', 'middlename', 'course', 'level', 'email', 'sessions')
    search_fields = ('firstname', 'middlename', 'lastname', 'username__username')
    list_filter = ('course', 'level')

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
    
@admin.register(Announcement, site=admin_site)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'date', 'superuser')
    list_display_links = ('title',)
    search_fields = ('superuser__username', 'superuser__registration__firstname', 'superuser__registration__middlename','superuser__registration__lastname',)
    list_filter = ('date', 'updated_at', SuperuserFilter)
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.superuser = request.user 
        super().save_model(request, obj, form, change)
        
@admin.register(AnnouncementComment, site=admin_site)
class AnnouncementCommentAdmin(admin.ModelAdmin):
    list_display = ('comment', 'date', 'announcement', 'user')
    list_display_links = ('comment',)
    search_fields = ('user__username', 'user__username', 'user__registration__firstname', 'user__registration__middlename','user__registration__lastname',)
    list_filter = ( 'announcement', 'date', 'updated_at',)

    # Change the verbose name directly in the model's _meta
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        self.model._meta.verbose_name = "Announcement Comment"
        self.model._meta.verbose_name_plural = "Announcement Comments"
        return qs

class PendingSitinFilter(admin.SimpleListFilter):
    title = _("Pending Sit-ins")
    parameter_name = "pending"

    def lookups(self, request, model_admin):
        return [("pending", _("Pending"))]

    def queryset(self, request, queryset):
        if self.value() == "pending":
            return queryset.filter(status="Pending")
        return queryset
    
class FinishedSitinFilter(admin.SimpleListFilter):
    title = _("Timed-out Sit-ins")
    parameter_name = "finished"

    def lookups(self, request, model_admin):
        return [("finished", _("Finished"))]

    def queryset(self, request, queryset):
        if self.value() == "finished":
            return queryset.filter(status="Finished")
        return queryset

class CurrentSitinFilter(admin.SimpleListFilter):
    title = _("Current Sit-ins")
    parameter_name = "approved"

    def lookups(self, request, model_admin):
        return [("approved", _("Approved"))]

    def queryset(self, request, queryset):
        if self.value() == "approved":
            return queryset.filter(status="Approved")
        return queryset

class BaseSitinAdmin(admin.ModelAdmin):
    change_list_template = 'admin/sitin_change_list.html'
    list_display = ('id', "get_user_idno", "get_fullname", "purpose", "lab_room", "status", "user__registration__sessions", "date")
    search_fields = ("user__registration__idno", "user__username", "user__registration__firstname", 
                     "user__registration__middlename", "user__registration__lastname")
    list_filter = ("programming_language", "purpose", "lab_room", "status", "date")

    def get_user_idno(self, obj):
        return obj.user.registration.idno if hasattr(obj.user, "registration") else None
    get_user_idno.short_description = "User ID"
    get_user_idno.admin_order_field = "user__registration__idno"

    def get_fullname(self, obj):
        if hasattr(obj.user, "registration"):
            reg = obj.user.registration
            return f"{reg.firstname} {reg.middlename} {reg.lastname}"
        return None
    get_fullname.short_description = "Fullname"

    def changelist_view(self, request, extra_context=None):
        # Aggregate statistics
        programming_language_stats = Sitin.objects.values("programming_language").annotate(count=Count("programming_language"))
        purpose_stats = Sitin.objects.values("purpose").annotate(count=Count("purpose"))
        lab_room_stats = Sitin.objects.values("lab_room").annotate(count=Count("lab_room"))

        # Pass stats to the template
        extra_context = extra_context or {}
        extra_context["programming_language_stats"] = programming_language_stats
        extra_context["purpose_stats"] = purpose_stats
        extra_context["lab_room_stats"] = lab_room_stats

        return super().changelist_view(request, extra_context=extra_context)

class SitinRequestsAdmin(BaseSitinAdmin):
    change_list_template = 'admin/sitin_change_list.html'

    def changelist_view(self, request, extra_context=None):
        # Aggregate statistics
        programming_language_stats = Sitin.objects.values("programming_language").annotate(count=Count("programming_language"))
        purpose_stats = Sitin.objects.values("purpose").annotate(count=Count("purpose"))
        lab_room_stats = Sitin.objects.values("lab_room").annotate(count=Count("lab_room"))

        # Pass stats to the template
        extra_context = extra_context or {}
        extra_context["programming_language_stats"] = programming_language_stats
        extra_context["purpose_stats"] = purpose_stats
        extra_context["lab_room_stats"] = lab_room_stats

        return super().changelist_view(request, extra_context=extra_context)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(status="pending")

    def get_model_perms(self, request):
        return {"view": True}  # Hide "Add" and "Delete" buttons

    def has_add_permission(self, request):
        return False

class CurrentSitinsAdmin(BaseSitinAdmin):
    change_list_template = 'admin/sitin_change_list.html'

    def changelist_view(self, request, extra_context=None):
        # Aggregate statistics
        programming_language_stats = Sitin.objects.values("programming_language").annotate(count=Count("programming_language"))
        purpose_stats = Sitin.objects.values("purpose").annotate(count=Count("purpose"))
        lab_room_stats = Sitin.objects.values("lab_room").annotate(count=Count("lab_room"))

        # Pass stats to the template
        extra_context = extra_context or {}
        extra_context["programming_language_stats"] = programming_language_stats
        extra_context["purpose_stats"] = purpose_stats
        extra_context["lab_room_stats"] = lab_room_stats

        return super().changelist_view(request, extra_context=extra_context)
    
    def get_queryset(self, request):
        return super().get_queryset(request).filter(status="approved")

    def get_model_perms(self, request):
        return {"view": True}  # Hide "Add" and "Delete" buttons
    
    def has_add_permission(self, request):
        return False
    
    def save_model(self, request, obj, form, change):
        """Reduce sessions by 1 when status is changed to 'finished'"""
        if obj.status == "finished" and obj.user.registration:
            regis = obj.user.registration
            if regis.sessions > 0:
                regis.sessions -= 1
                regis.save()
        super().save_model(request, obj, form, change)
    
class FinishedSitinsAdmin(BaseSitinAdmin):
    change_list_template = 'admin/sitin_change_list.html'

    def changelist_view(self, request, extra_context=None):
        # Aggregate statistics
        programming_language_stats = Sitin.objects.values("programming_language").annotate(count=Count("programming_language"))
        purpose_stats = Sitin.objects.values("purpose").annotate(count=Count("purpose"))
        lab_room_stats = Sitin.objects.values("lab_room").annotate(count=Count("lab_room"))

        # Pass stats to the template
        extra_context = extra_context or {}
        extra_context["programming_language_stats"] = programming_language_stats
        extra_context["purpose_stats"] = purpose_stats
        extra_context["lab_room_stats"] = lab_room_stats

        return super().changelist_view(request, extra_context=extra_context)
    
    def get_queryset(self, request):
        return super().get_queryset(request).filter(status="finished")

    def get_model_perms(self, request):
        return {"view": True}  # Hide "Add" and "Delete" buttons
    
    def has_add_permission(self, request):
        return False

# Proxy models
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

admin_site.register(Sitin, BaseSitinAdmin)
admin_site.register(SitinRequests, SitinRequestsAdmin)
admin_site.register(CurrentSitins, CurrentSitinsAdmin)
admin_site.register(FinishedSitins, FinishedSitinsAdmin)

    
# admin
# ganymede14337
