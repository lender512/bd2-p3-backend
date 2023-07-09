from django.contrib.auth.models import User, Group
from rest_framework import serializers
import os

from quickstart.models import FaceVector


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']

class FaceVectorSerializer(serializers.HyperlinkedModelSerializer):

    def get_path(self, obj):
        path = "129.146.71.229:8000/media/images"
        name = "_".join(obj.name.split("_")[:-1])
        return os.path.join(path, name, obj.name)

    #add custom field image_route
    path = serializers.SerializerMethodField('get_path')


    class Meta:
        model = FaceVector
        fields = ['name', 'distance', 'path']
