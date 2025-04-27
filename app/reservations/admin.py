from django.contrib import admin
from backend.admin import admin_site
from sitins.admin import BaseSitinAdmin
from sitins.models import Sitin
from .models import LabRoom, Computer

class ComputersAdmin(admin.ModelAdmin):
    list_display = ('pc_number', 'operating_system', 'processor', 'ram_amount_in_mb', 'is_available', 'lab_room')
    list_display_links = ('pc_number',)
    list_filter = ('lab_room',)
    actions = ['set_available',]

    def set_available(self, request, queryset):
        for pc in queryset:
            pc.is_available = not pc.is_available
            pc.save()
            self.message_user(request, f"PC {pc.pc_number} is now {"'available'" if pc.is_available else "'not available'"}.")
    set_available.short_description = "Set available/unavailable"

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

class SitinRequestsAdmin(BaseSitinAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(request_date__isnull=False)
    
class SitinRequestsProxy(Sitin):
    class Meta:
        proxy = True
        verbose_name = "Sit-in Request"
        verbose_name_plural = "Sit-in Requests"
        
admin_site.register(SitinRequestsProxy, SitinRequestsAdmin)