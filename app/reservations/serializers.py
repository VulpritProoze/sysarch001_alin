from sitins.models import Sitin 
from .models import LabRoom, Computer, SitinRequest
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

class SitinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sitin
        fields = ['id', 'purpose', 'programming_language', 'lab_room', 'sitin_details', 'sitin_date', 'request_date', 'user']

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
        
    def validate(self, data):
        request = self.context.get('request')

        pc = data.get('pc')
        user = request.user if request else None
        
        # Validate if pc is available
        if pc and not pc.is_available:
            raise ValidationError({ 'pc': 'This computer is currently unavailable for reservation' })

        # Validate if user already has a cuurently sitin requestt
        if user and Sitin.objects.filter(user=user, status='approved').exists():
            raise ValidationError({ 'user': 'User already has an approved sit-in. Two approved sit-ins at once is not allowed.'})
        
        return data