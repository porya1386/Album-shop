from rest_framework import serializers
from .models import Album_image
class Album_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Album_image
        fields = "__all__"
        exclude = 'slug'