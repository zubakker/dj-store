from django.contrib.auth.models import User, Group
from rest_framework import serializers

from store.models import Tag, Product

class UserSerializer(serializers.HyperlinkedModelSerializer):
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
        )
        return user
    '''
    def update(self, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        '''

    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'password', 'groups', 'first_name', 'last_name']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']



class TagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tag
        fields = ['url', 'name']

class ProductSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Product
        fields = [
                    'url', 
                    'name', 
                    'price', 
                    'description', 
                    'vendor_code', 
                    'stock',
                    'tags',
                    'author'
                 ]
