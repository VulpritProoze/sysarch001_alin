from django.db import models
from django.contrib.auth.models import User

# Reservation tables
class LabRoom(models.Model):
    room_number = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    capacity = models.IntegerField(null=True, blank=True)
    is_available = models.BooleanField(default=False, blank=True, null=True)
    administrated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={ 'is_superuser': True })

    def __str__(self):
        return f"Lab #{self.room_number}, administrated by {self.administrated_by or 'N/A'}"

class Computer(models.Model):
    pc_number = models.IntegerField(null=True, blank=True)
    operating_system = models.CharField(max_length=50, blank=True, null=True)
    processor = models.CharField(max_length=50, blank=True, null=True)
    ram_amount_in_mb = models.IntegerField(null=True, blank=True)
    is_available = models.BooleanField(default=False, blank=True, null=True)
    installed_at = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    lab_room = models.ForeignKey(LabRoom, on_delete=models.CASCADE)

    def __str__(self):
        return f"PC #{self.pc_number} at Lab #{self.lab_room.room_number}"