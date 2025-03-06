from django.contrib import admin
from django.contrib.auth.models import User
from django.template.response import TemplateResponse
from .models import Registration, Announcement, AnnouncementComment, Sitin
from .choices import SITIN_STATUS_CHOICES

admin.site.site_header = "CCS Sitin Admin"
admin.site.index_title = "Welcome to CCS Sitin Admin Panel"

def custom_admin_view(request):
    context = admin.site.each_context(request)  # Get default admin context
    context.update({
        'total_users': User.objects.count(),
        'total_announcements': Announcement.objects.count(),
    })
    return TemplateResponse(request, "admin/index.html", context)

admin.site.index_template = "admin/index.html"

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    class Meta:
        verbose_name_plural = "Users"
    
    list_display = ('idno', 'username', 'firstname', 'lastname', 'middlename', 'course', 'level', 'email', 'address', 'profilepicture_og','profilepicture_lg', 'profilepicture_md', 'profilepicture_sm', 'profiledescription')
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
    
@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'image', 'date', 'updated_at', 'superuser')
    list_display_links = ('title',)
    search_fields = ('superuser__username', 'superuser__registration__firstname', 'superuser__registration__middlename','superuser__registration__lastname',)
    list_filter = ('date', 'updated_at', SuperuserFilter)
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.superuser = request.user 
        super().save_model(request, obj, form, change)
        
@admin.register(AnnouncementComment)
class AnnouncementCommentAdmin(admin.ModelAdmin):
    list_display = ('comment', 'date', 'updated_at', 'announcement', 'user')
    list_display_links = ('comment',)
    search_fields = ('user__username', 'user__username', 'user__registration__firstname', 'user__registration__middlename','user__registration__lastname',)
    list_filter = ( 'announcement', 'date', 'updated_at',)
    
    class Meta:
        verbose_name = 'Comment(Announcements)'
        verbose_name_plural = 'Comments(Announcements)'
    
@admin.register(Sitin)
class SitinAdmin(admin.ModelAdmin):
    list_display = ('get_user_idno', 'user__username', 'get_fullname', 'purpose', 'programming_language', 'lab_room', 'sitin_details', 'status', 'date')
    search_fields = ('user__registration__idno', 'user__username', 'user__registration__firstname', 'user__registration__middlename','user__registration__lastname')
    list_filter = ('programming_language', 'purpose', 'lab_room', 'status', 'date')

    def get_user_idno(self, obj):
        return obj.user.registration.idno if hasattr(obj.user, 'registration') else None
    get_user_idno.short_description = 'User ID'
    get_user_idno.admin_order_field = 'user__registration__idno'
    
    def get_fullname(self, obj):
        if hasattr(obj.user, 'registration'):
            reg = obj.user.registration 
            return f"{reg.firstname} {reg.middlename} {reg.lastname}"
        return None
    get_fullname.short_description = 'Fullname'
    
    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "status":
            kwargs["choices"] = SITIN_STATUS_CHOICES
        return super().formfield_for_choice_field(db_field, request, **kwargs)
    
# admin
# ganymede14337
