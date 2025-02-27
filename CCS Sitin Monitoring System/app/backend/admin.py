from django.contrib import admin
from django.db import models
from django.forms import Textarea
from .models import Registration, Announcement, AnnouncementComment

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    class Meta:
        verbose_name_plural = "Users"
    
    list_display = ('idno', 'username', 'firstname', 'lastname', 'middlename', 'course', 'level', 'email', 'address', 'profilepicture_og','profilepicture_lg', 'profilepicture_md', 'profilepicture_sm', 'profiledescription')
    search_fields = ('firstname', 'lastname', 'email', 'username__username')
    list_filter = ('course', 'level')
    list_editable = ('firstname', 'lastname', 'middlename', 'course', 'level', 'email', 'address', 'profilepicture_og', 'profilepicture_lg', 'profilepicture_md', 'profilepicture_sm', 'profiledescription')

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 40})},
    }
    
@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('id','title', 'content', 'image', 'date', 'updated_at', 'superuser')
    search_fields = ('title', 'content', 'superuser__username')
    list_filter = ('date', 'updated_at')
    list_editable = ('title','content', 'image') 
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.superuser = request.user 
        super().save_model(request, obj, form, change)
        
@admin.register(AnnouncementComment)
class AnnouncementCommentAdmin(admin.ModelAdmin):
    list_display = ('id','comment', 'date', 'updated_at', 'announcement', 'user')
    search_fields = ('comment', 'user__username', 'announcement__title')
    list_filter = ('user', 'announcement', 'date', 'updated_at',)
    list_editable = ('comment','announcement', 'user')
    
# admin
# ganymede14337
