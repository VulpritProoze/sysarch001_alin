from django.contrib import admin
from django.db.models import Q
from backend.admin import admin_site
from sitins.admin import BaseSitinAdmin
from sitins.models import Sitin
from notifications.notifications import send_notification
from .models import LabRoom, Computer
from django.utils import timezone
from django.contrib import messages
from .tasks import schedule_reservation_reminder
class ComputersAdmin(admin.ModelAdmin):
    list_display = ('pc_number', 'operating_system', 'processor', 'ram_amount_in_mb', 'is_available', 'lab_room')
    list_display_links = ('pc_number',)
    list_filter = ('lab_room',)
    actions = ['set_available', 'set_unavailable',]

    def set_available(self, request, queryset):
        for pc in queryset:
            pc.is_available = True
            pc.save()
            self.message_user(request, f"PC {pc.pc_number} is now available.")
    set_available.short_description = "Set available"
    
    def set_unavailable(self, request, queryset):
        for pc in queryset:
            pc.is_available = False
            pc.save()
            self.message_user(request, f"PC {pc.pc_number} is now unavailable.")
    set_unavailable.short_description = "Set unavailable"

admin_site.register(Computer, ComputersAdmin)

class InlineComputersAdmin(admin.StackedInline):
    model = Computer
    fields = ('pc_number', 'operating_system', 'processor', 'ram_amount_in_mb', 'is_available', 'lab_room')
    extra = 3

class LabRoomsAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'name', 'capacity', 'is_available', 'administrated_by')
    list_display_links = ('room_number',)
    inlines = (InlineComputersAdmin,)

    def has_add_permission(self, request, obj=None):
        return False

admin_site.register(LabRoom, LabRoomsAdmin)

class ReservationRequestsAdmin(BaseSitinAdmin):
    change_list_template = 'admin/reservations/reservationrequest_changelist.html'
    actions = ['approve_request', 'reject_request',]
    
    def get_queryset(self, request):
        return super().get_queryset(request).filter(request_date__isnull=False, status='none')
    
    def approve_request(self, request, queryset):
        queryset = queryset.select_related(
            'user'
        ).prefetch_related(
            'sitinrequest_set',
            'sitinrequest_set__pc',
            'sitinrequest_set__lab_room'
        )
        
        for sitin in queryset:
            sitin.approval_date = timezone.now()
            sitin.status = 'approved'
            sitin.save()
            self.message_user(request, f"{sitin.user.username}'s sitin request has been successfully approved.")

            # Send notification to user that his/her request has been approved
            user = sitin.user
            sitinrequest = sitin.sitinrequest_set.first()
            message = f'Your reservation request (ID/{sitinrequest.id}) for LAB/{sitinrequest.lab_room.room_number}, PC/{sitinrequest.pc.pc_number} has been approved.'
            url = f'/reservations/#sitinrequest-id-{sitinrequest.id}'
            sitinrequest.pc.is_available = not sitinrequest.pc.is_available
            sitinrequest.pc.save()
            
            send_notification(user, message, url, 'sitin')
            schedule_reservation_reminder(sitinrequest.id)
            
            
    def reject_request(self, request, queryset):
        for sitin in queryset:
            sitin.status = 'rejected'
            sitin.save()
            self.message_user(request, f"{sitin.user.username}'s sitin request has been successfully rejected.", messages.WARNING)
            
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
class ReservationLogsAdmin(BaseSitinAdmin):
    def get_queryset(self, request):
        queryset = super().get_queryset(request).filter(Q(request_date__isnull=False) & Q(status='finished') |  Q(status='rejected'))
        return queryset
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
class ReservationRequestProxy(Sitin):
    class Meta:
        proxy = True
        verbose_name = "Reservation request"
        verbose_name_plural = "Reservation requests"
        
class ReservationLogProxy(Sitin):
    class Meta:
        proxy = True 
        verbose_name = "Reservation log"
        verbose_name_plural = "Reservation logs"
        
admin_site.register(ReservationRequestProxy, ReservationRequestsAdmin)
admin_site.register(ReservationLogProxy, ReservationLogsAdmin)