from rest_framework import serializers
from .models import Sitin

class SitinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sitin
        fields = '__all__'
        read_only_fields = ['user']