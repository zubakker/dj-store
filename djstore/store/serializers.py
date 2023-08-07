from django.contrib.auth.models import User, Group
from rest_framework import serializers

from store.models import Tag, Product, Cart

class UserSerializer(serializers.HyperlinkedModelSerializer):
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
        )
        return user
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
                    'tags'
                 ]

class CartSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.CharField(source='user.username')
    def update(self, instance, item, amount):
        if item in list(instance.items):
            instance.items[item] += amount
        else:
            instance.items[item] = amount
        return instance
    def remove(self, instance, item, amount):
        if item not in list(instance.items):
            return instance
        if amount == 'ALL':
            del instance.items[item]
        else:
            instance.items[item] -= int(amount)
            if instance.items[item] <= 0:
                del instance.items[item]
        return instance
    def delete(self, instance):
        instance.items = dict()
        return instance
        

    class Meta:
        model = Cart
        fields = [
                    'user',
                    'items'
                 ]
