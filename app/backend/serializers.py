from rest_framework import serializers
from .models import Registration, Announcement, AnnouncementComment, SitinSurvey

class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        fields = '__all__'  # Include all fields
        read_only_fields = ['idno', 'username'] # Update only
        
class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = '__all__'  # Include all fields

class AnnouncementCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnouncementComment
        fields = '__all__'  # Include all fields
        read_only_fields = ['user', 'announcement']

class SitinSurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = SitinSurvey 
        fields = '__all__'
        read_only_fields = ['user']