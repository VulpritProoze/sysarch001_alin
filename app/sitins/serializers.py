from rest_framework import serializers
from .models import Sitin

class SitinFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sitin
        fields = '__all__'
        read_only_fields = ['user']