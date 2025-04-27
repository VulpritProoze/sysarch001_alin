from sitins.models import Sitin 
from .models import LabRoom, Computer, SitinRequest
from rest_framework import serializers

class SitinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sitin
        fields = ['id', 'purpose', 'programming_language', 'lab_room', 'sitin_details', 'request_date', 'user']

class LabRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabRoom
        fields = ['id', 'room_number', 'name', 'capacity']

class ComputerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Computer
        fields = ['id', 'pc_number', 'operating_system', 'processor']
        
class SitinRequestSerializer(serializers.ModelSerializer): 
    class Meta:
        model = SitinRequest
        fields = ['lab_room', 'pc', 'request_date']