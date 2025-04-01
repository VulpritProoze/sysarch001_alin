from rest_framework import serializers
from .models import Registration, Announcement, AnnouncementComment, Sitin, SitinSurvey

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

class SitinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sitin
        fields = '__all__'
        read_only_fields = ['user']
        
    # Custom validation
    def validate(self, data):
        request = self.context.get('request')
        instance = self.instance    # User passed from front-end
        if instance:
            if instance.user != request.user:
                raise serializers.ValidationError({"Sitin Request": "Only the user related to this sitin can update this."})
        # if instance.purpose == '' or instance.programming_language == '' or instance.lab_room == '' or instance.sitin_details == '' or not instance.user:
        #     raise serializers.ValidationError({"Sitin Request": "None of the sitin request fields can be empty."})
        if data.get('purpose') == '':
            raise serializers.ValidationError({"Sitin Request": "None of the sitin request fields can be empty."})
        return data
    
class SitinFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sitin
        fields = '__all__'
        read_only_fields = ['user']

class SitinSurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = SitinSurvey 
        fields = '__all__'
        read_only_fields = ['user']