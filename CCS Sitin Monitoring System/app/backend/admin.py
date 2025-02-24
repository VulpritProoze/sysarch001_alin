from django.contrib import admin
from django.db import models
from django.forms import Textarea, FileInput, TextInput
from .models import Registration, Announcement

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    class Meta:
        verbose_name_plural = "Users"
    
    list_display = ('idno', 'username', 'firstname', 'lastname', 'middlename', 'course', 'level', 'email', 'address', 'profilepicture', 'profiledescription')
    search_fields = ('firstname', 'lastname', 'email', 'username__username')
    list_filter = ('course', 'level')
    list_editable = ('firstname', 'lastname', 'middlename', 'course', 'level', 'email', 'address', 'profilepicture', 'profiledescription')

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 40})},
    }
    
@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'date', 'updated_at', 'superuser')
    list_display_links = ('title',)  # Add this line
    search_fields = ('title', 'content', 'superuser__username')
    list_filter = ('date', 'updated_at')
    list_editable = ('content', 'superuser')  # Remove 'title' from list_editable

    def save_model(self, request, obj, form, change):
        if not obj.superuser:  # Only set if it's not already assigned
            obj.superuser = request.user
        obj.save()
    
# admin
# ganymede14337
