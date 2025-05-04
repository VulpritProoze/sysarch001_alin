from django.contrib import admin
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.contrib import messages
from django.urls import path
from django.urls.resolvers import URLPattern
from backend.admin import admin_site 
from backend.custom_changelist import CustomChangeList
from .models import Sitin
from django.db.models import Q
        
class BaseSitinAdmin(admin.ModelAdmin):
    list_display = ("get_user_idno", "get_fullname", "purpose", "lab_room", "status", "get_user_points", "is_rewarded", "get_user_sessions", "request_date", "get_formatted_login_date", "get_formatted_logout_date")
    search_fields = ("user__registration__idno", "user__username", "user__registration__firstname", 
                     "user__registration__middlename", "user__registration__lastname")
    list_filter = ("sitin_date",'logout_date')
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

    def get_formatted_login_date(self, obj):
        return obj.sitin_date  # You can format the date here if needed

    get_formatted_login_date.short_description = "Time-in"  # Change the display name here
    get_formatted_login_date.admin_order_field = "sitin_date"  # Ensure the field is sortable by date

    def get_formatted_logout_date(self, obj):
        return obj.logout_date  # You can format the date here if needed
    get_formatted_logout_date.short_description = "Time-out"  # Change the display name here
    get_formatted_logout_date.admin_order_field = "logout_date"  # Ensure the field is sortable by date
    
    def get_user_sessions(self, obj):
        return obj.user.registration.sessions
    get_user_sessions.short_description = "Sessions"
    get_user_sessions.admin_order_field = 'user__registration__sessions'
    
    def get_user_points(self, obj):
        return obj.user.registration.points 
    get_user_points.short_description = "Points"
    get_user_points.admin_order_field = 'user__registration__points'

class SearchSitinsInline(admin.StackedInline):
    model = Sitin
    extra = 0
    can_delete = False
    fieldsets = (
        (None, {'fields': ('purpose', 'programming_language', 'lab_room', 'sitin_details', 'status',)}),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request).filter(Q(status='approved') | Q(status='none'))
        self.model._meta.verbose_name = "Add Sitin"
        self.model._meta.verbose_name_plural = "Add Sitins"
        return qs
    
    def formfield_for_choice_field(self, db_field, request, **kwargs):
        # Customize the choices for the 'status' field
        if db_field.name == 'status':
            # Modify the choices dynamically
            kwargs['choices'] = (
                ('none', 'Not Sitin'),
                ('approved', 'Approved'),
                ('rejected', 'Rejected'),
            )
        return super().formfield_for_choice_field(db_field, request, **kwargs)

# Search Sitins (admin can search for student to sitin)
# Model: User (as proxy)
class SearchSitinsAdmin(admin.ModelAdmin):
    change_list_template = 'admin/backend/sitin/searchsitins_change_list.html'
    change_form_template = 'admin/backend/sitin/change_form/searchsitins_change_form.html'
    inlines = (SearchSitinsInline,)
    list_display = ('get_idno', 'get_fullname', 'get_points', 'get_sessions', 'get_sitinscount')
    list_display_links = ('get_idno',)
    list_filter = ('sitin__sitin_date', 'sitin__logout_date',)
    search_fields = ('registration__idno',)
    fieldsets = (
        ('Personal info', {'fields': ('registration__idno', 'registration__firstname', 'registration__middlename', 'registration__lastname', 'registration__sessions')}),
    )     
                
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            'registration',
        )
    
    # Override default saving behavior on change_form
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Set sitin_date on sitin inline to now
        obj.sitin_set.all().update(sitin_date=timezone.now())

    def get_idno(self, obj):
        return obj.registration.idno
    get_idno.short_description = "Student ID"
    get_idno.admin_order_field = "registration__idno"
    
    def get_fullname(self, obj):
        return f"{obj.registration.lastname}, {obj.registration.firstname} {obj.registration.middlename}"
    get_fullname.short_description = "Fullname"
    get_fullname.admin_order_field = "registration__lastname"  
    
    def get_points(self, obj):
        return obj.registration.points
    get_points.short_description = "Points Earned"
    get_points.admin_order_field = "registration__points"
    
    def get_sitinscount(self, obj):
        return obj.registration.sitins_count
    get_sitinscount.short_description = "# of Sitins"
    get_sitinscount.admin_order_field = "registration__sitins_count"
    
    def get_sessions(self, obj):
        return obj.registration.sessions
    get_sessions.short_description = "Sessions"
    get_sessions.admin_order_field = "registration__sessions"

    def get_model_perms(self, request):
        return {"view": True}  # Hide "Add" and "Delete" buttons

    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, object=None):
        return False
    
    def get_readonly_fields(self, request, obj=None):
        # Make all fields in the change form read-only
        if obj:  # obj is not None, so we're editing an existing object
            return ['registration__idno', 'registration__firstname', 'registration__middlename', 'registration__lastname', 'registration__sessions']
        return self.readonly_fields
        
# Current Sitins (admin can view students who has currently sitin)
class CurrentSitinsAdmin(BaseSitinAdmin):
    change_list_template = 'admin/backend/sitin/logout_change_list.html'
    list_display = ("get_user_idno", "get_fullname", "purpose", "lab_room", "get_user_points", "is_rewarded", "get_user_sessions", "get_formatted_login_date",)
    list_display_links = ('get_user_idno',)
    list_filter = ('sitin_date',)
    fieldsets = (
        (None, {'fields': ('purpose', 'programming_language', 'lab_room', 'sitin_details', 'status', 'sitin_date', 'user',)}),
    )
    actions = ['logout_student', 'assign_points',]
    
    def get_changelist(self, request, **kwargs):
        return CustomChangeList
    
    def get_queryset(self, request):
        return super().get_queryset(request).filter(status="approved")
    
    # Disable change_form view
    def get_urls(self):
        # Get the default URLs
        urls = super().get_urls()
        # Filter out the change view URL pattern
        urls = [ url for url in urls if not (isinstance(url, URLPattern) and url.pattern._route == '<path:object_id>/change/')]
        return urls

    def get_model_perms(self, request):
        return {"view": True}  # Hide "Add" and "Delete" buttons
    
    def has_change_permission(self, request, obj=False):
        return False
    
    def has_add_permission(self, request):
        return False
    
    def assign_points(self, request, queryset):
        queryset = queryset.select_related(
            'user',
            'user__registration'
        )
        for sitin in queryset:
            username = sitin.user.username if sitin.user else 'N/A'
            if not sitin.is_rewarded:
                if hasattr(sitin.user, 'registration'):
                    sitin.user.registration.points += 1
                    sitin.user.registration.save()
                    
                    sitin.is_rewarded = True 
                    sitin.save()
                    
                    
                    self.message_user(request, f"{username} has been rewarded 1 point.")
            else:
                self.message_user(request, f"{username} has already been rewarded.", messages.ERROR)
    assign_points.short_description = "Reward student(s)"
    
    def logout_student(self, request, queryset):
        queryset = queryset.select_related(
            'user__registration',
        ).prefetch_related(
            'sitinrequest_set',
            'sitinrequest_set__pc'    
        )
        
        for sitin in queryset:
            sitin.logout_date = timezone.now()  # Set logout date to current time
            sitin.status = 'finished'   # Set sitin status to finished
            sitin.save()
            
            if hasattr(sitin.user, 'registration'):
                registration = sitin.user.registration
                registration.sessions -= 1   # Reduce user session by 1 everytime they're logged out
                registration.sitins_count += 1 # Increment sitins_count by 1 everytime they're logged out

                if registration.points % 3 == 0: # Only award one point each time
                    registration.sessions += 1
                
                registration.save()

            sitinrequest = sitin.sitinrequest_set.first()
            if sitinrequest and sitinrequest.pc:
                sitinrequest.pc.is_available = not sitinrequest.pc.is_available
                sitinrequest.pc.save()

        self.message_user(request, f"Student/s has been logged out.")
    logout_student.short_description = "Logout selected students"
    
# Sit-in History (admin can view students who has been timed-out by admin, and admin can also generate reports into pdf, csv, excel, and print)
class FinishedSitinsAdmin(BaseSitinAdmin):    
    list_display = ("get_user_idno", "get_fullname", "purpose", "lab_room", "status", "get_user_points", "is_rewarded", "get_user_sessions", "get_formatted_logout_date",)
    change_list_template = "admin/backend/sitin/timedout_change_list.html"
    fieldsets = (
        (None, {'fields': ('purpose', 'programming_language', 'lab_room', 'sitin_details', 'status', 'sitin_date', 'logout_date', 'user', 'feedback')}),
    )

    def get_model_perms(self, request):
        return {"view": True}  # Hide "Add" and "Delete" buttons
    
    def has_add_permission(self, request):
        return False
      
    def get_queryset(self, request):
        qs = super().get_queryset(request).filter(status="finished")
        return qs
    
    # # Disable change_form view
    # def get_urls(self):
    #     # Get the default URLs
    #     urls = super().get_urls()
    #     # Filter out the change view URL pattern
    #     urls = [ url for url in urls if not (isinstance(url, URLPattern) and url.pattern._route == '<path:object_id>/change/')]
    #     return urls
    
    def has_change_permission(self, request, obj=False):
        return False
    
    def has_delete_permission(self, request, obj=False):
        return False

class SearchSitins(User):
    class Meta:
        proxy = True 
        verbose_name = "Search student to sitin"
        verbose_name_plural = "Search student to sitin"  # Plural version

# All Sitins
class AllSitins(Sitin):
    class Meta:
        proxy = True
        verbose_name = "All sitins"
        verbose_name_plural = "All sitins"  # Plural version

# Current Sitins
class CurrentSitins(Sitin):
    class Meta:
        proxy = True
        verbose_name = "Currently sit-in"
        verbose_name_plural = "Currently sit-ins"

# Sit-in History
class FinishedSitins(Sitin):
    class Meta:
        proxy = True
        verbose_name = "Sit-in history"
        verbose_name_plural = "Sit-in history"

admin_site.register(SearchSitins, SearchSitinsAdmin)
admin_site.register(CurrentSitins, CurrentSitinsAdmin)
admin_site.register(FinishedSitins, FinishedSitinsAdmin)

