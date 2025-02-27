from rest_framework import serializers
from .models import Registration, Announcement, AnnouncementComment

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
        extra_kwargs = {'user': {'read_only': True}, 'announcement': {'read_only': True}}    # Make user,announcement read-only (ignore post requests that attempts to append 'user', 'announcement')
        
    def validate(self, data):
        request = self.context.get('request')

        if self.instance:
            if self.instance.user != request.user:
                raise serializers.ValidationError("Only the user related to this comment can update/delete this.")
        
        return data    