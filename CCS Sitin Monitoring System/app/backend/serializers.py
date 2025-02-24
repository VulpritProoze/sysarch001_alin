from rest_framework import serializers
from .models import Registration, Announcement, AnnouncementComment

class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        fields = '__all__'  # Include all fields
        read_only_fields = ['idno', 'username'] # Update only
        
class AnnouncementCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnouncementComment
        fields = '__all__'  # Include all fields