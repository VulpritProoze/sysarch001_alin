from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .admin_site import CustomAdminSite
from .models import Registration, Announcement, AnnouncementComment, SitinSurvey, SurveyResponse, LabResource

# Instantiating custom admin site
admin_site = CustomAdminSite(name='custom_admin')
admin_site.site_header = "CCS Sitin Administration"
admin_site.site_title = "CCS Sitin Administration"
admin_site.index_title = "Welcome to the Sitin Administration Panel of CCS Department"

# @admin.register(Registration, site=admin_site)
class RegistrationInline(admin.StackedInline):
    model = Registration 
    extra = 1
    can_delete = False
    
    # Change the verbose name directly in the model's _meta
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        self.model._meta.verbose_name = "User Detail"
        self.model._meta.verbose_name_plural = "User Details"
        return qs

# @admin.site.unregister(User)
class CustomUserAdmin(UserAdmin):
    change_list_template = 'admin/auth/user_change_list.html'
    list_display = ('username', 'get_idno', 'get_firstname', 'get_middlename', 'get_lastname','get_sessions', 'is_staff')
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
    
    def get_idno(self, obj):
        return obj.registration.idno
    get_idno.short_description = "Student ID"
    get_idno.admin_order_field = "registration__idno"
    
    def get_firstname(self, obj):
        return obj.registration.firstname
    get_firstname.short_description = "Firstname"
    get_firstname.admin_order_field = "registration__firstname"
    
    def get_middlename(self, obj):
        return obj.registration.middlename
    get_middlename.short_description = "Middlename"
    get_middlename.admin_order_field = "registration__middlename"
    
    def get_lastname(self, obj):
        return obj.registration.lastname
    get_lastname.short_description = "Lastname"
    get_lastname.admin_order_field = "registration__lastname"
    
    def get_sessions(self, obj):
        return obj.registration.sessions
    get_sessions.short_description = "Sessions"
    get_sessions.admin_order_field = "registration__sessions"
    
    actions = ['reset_sessions_to_30']
    
    def reset_sessions_to_30(self,request, queryset):
        updated_count = 0
        for user in queryset:
            if hasattr(user, 'registration'):
                user.registration.sessions = 30
                user.registration.save()
                updated_count += 1
        self.message_user(request, f"{updated_count} user(s) had their sessions reset back to 30.")
    reset_sessions_to_30.short_description = "Reset selected users' session back to 30"

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
    
class SurveyResponseInline(admin.StackedInline):
    model = SurveyResponse
    extra = 0
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
class SitinSurveyAdmin(admin.ModelAdmin):
    list_display = ('get_idno', 'get_fullname', 'get_sessions', 'status')
    list_display_links = ('get_idno',)
    list_filter = ('created_at', 'updated_at')    
    inlines = (SurveyResponseInline,)
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def get_idno(self, obj):
        return obj.created_by.registration.idno
    get_idno.short_description = "Student ID"
    get_idno.admin_order_field = "created_by__registration__idno"
    
    def get_fullname(self, obj):
        return f"{obj.created_by.registration.lastname}, {obj.created_by.registration.firstname} {obj.created_by.registration.middlename}"
    get_fullname.short_description = "Fullname"
    get_fullname.admin_order_field = "created_by__registration__lastname"  
    
    def get_sessions(self, obj):
        return obj.created_by.registration.sessions
    get_sessions.short_description = "Sessions"
    get_sessions.admin_order_field = "created_by__registration__sessions"
    
admin_site.register(SitinSurvey, SitinSurveyAdmin)    
    
# @admin.register(Announcement, site=admin_site)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'date', 'superuser')
    list_display_links = ('title',)
    search_fields = ('superuser__username', 'superuser__registration__firstname', 'superuser__registration__middlename','superuser__registration__lastname',)
    list_filter = ('date', 'updated_at', SuperuserFilter)
    
    # Make the logged-in superuser the author of announcement
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.superuser = request.user 
        super().save_model(request, obj, form, change)

    # Disable option of making other superuser the author
    def get_fields(self, request, obj=None):
        # Exclude 'superuser' in the add form (obj is None)
        fields = super().get_fields(request, obj)
        if not obj:  # Add form
            fields = [f for f in fields if f != 'superuser']
        return fields

    def get_readonly_fields(self, request, obj=None):
        # Make all fields in the change form read-only
        if obj:  # obj is not None, so we're editing an existing object
            return ['superuser',]
        return self.readonly_fields
    
class AnnouncementCommentInline(admin.StackedInline):
    model = AnnouncementComment 
    fields = ('user', 'comment', 'date', 'updated_at')
    readonly_fields = ('date', 'updated_at',)
    extra = 0
    
    def has_add_permission(self, request, obj=None):
        return False

class ExtendedAnnouncementAdmin(AnnouncementAdmin):
    inlines = (AnnouncementCommentInline,)    

admin_site.register(Announcement, ExtendedAnnouncementAdmin)

class LabResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'is_enabled', 'created_at')
    link_display_links = ('title',)
    search_filter = ('created_at')
    actions = ['toggle_enable_resource',]

    
    # Make the logged-in superuser the author of announcement
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user 
        super().save_model(request, obj, form, change)
        
    def get_readonly_fields(self, request, obj=None):
        # Make all fields in the change form read-only
        if obj:  # obj is not None, so we're editing an existing object
            return ['created_by',]
        return self.readonly_fields
    
    # Disable option of making other superuser the author
    def get_fields(self, request, obj=None):
        # Exclude 'superuser' in the add form (obj is None)
        fields = super().get_fields(request, obj)
        if not obj:  # Add form
            fields = [f for f in fields if f != 'created_by']
        return fields
        
    def toggle_enable_resource(self, request, queryset):
        if queryset.exists:
            for resource in queryset:
                resource.is_enabled = not resource.is_enabled
                resource.save()
            self.message_user(request, f"Resource/s have been enabled/disabled.")
    toggle_enable_resource.short_description = "Enable/disable selected resource"
    
admin_site.register(LabResource, LabResourceAdmin)


# admin
# ganymede14337
