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
        fields = ['id', 'name']

class ProductSerializer(serializers.HyperlinkedModelSerializer):
    tags = TagSerializer(many=True, read_only='True')
    class Meta:
        model = Product
        fields = [
                    'id',
                    'name', 
                    'price', 
                    'description', 
                    'vendor_code', 
                    'stock',
                    'tags'
                 ]
class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()
    amount = serializers.IntegerField(required=False)
    class Meta:
        model = Product
        fields = ['product_id', 'amount']

class TokenSerializer(serializers.Serializer):
    token = serializers.CharField()
class UserAuthSerializer( serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
class UserUpdateSerializer( serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'email', 'groups', 'first_name', 'last_name']


class CartSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.CharField(source='user.username')
    def update(self, instance, item, amount):
        item_url = item['url']
        for i in range(len(instance.items)):
            if instance.items[i]['url'] == item_url:
                instance.items[i]['amount'] += amount
                item_cum_pr = float(instance[i]['price'])*amount
                instance.items[i]['cum_price'] += item_cum_pr
                instance.items[i]['cum_price'] = round(instance[i]['cum_price'], 2)

                instance.cum_price = item_cum_pr + float(instance.cum_price)
                break
        else:
            item_dict = {'url': item_url, 'amount': amount}
            item_dict.update(item)
            item_cum_pr = round(float(item_dict['price'])*amount, 2)
            item_dict['cum_price'] = item_cum_pr

            instance.cum_price = item_cum_pr + float(instance.cum_price)
            instance.items.append(item_dict)
        instance.cum_price = round(instance.cum_price, 2)
        return instance
    def remove(self, instance, item, amount):
        for i in range(len(instance.items)):
            if instance.items[i]['id'] == int(item):
                if amount == 'ALL':
                    item_cum_pr = instance.items[i]['amount'] * float(instance.items[i]['price'])
                    instance.cum_price = float(instance.cum_price) - item_cum_pr  
                    del instance.items[i]
                else:
                    instance.items[i]['amount'] -= int(amount)
                    item_cum_pr = float(instance[i]['price'])*amount
                    instance.items[i]['cum_price'] -= item_cum_pr
                    instance.items[i]['cum_price'] = round(instance[i]['cum_price'], 2)

                    if instance.items[i]['amount'] <= 0:
                        item_cum_pr = instance.items[i]['amount'] * float(instance.items[i]['price'])
                        instance.cum_price = float(instance.cum_price) - item_cum_pr  
                        del instance.items[i]
                    else:
                        instance.cum_price = float(instance.cum_price) - item_cum_pr  
                break
        instance.cum_price = round(instance.cum_price, 2)
        return instance
    def delete(self, instance):
        instance.items = list()
        instance.cum_price = 0
        return instance
        

    class Meta:
        model = Cart
        fields = [
                    'user',
                    'items',
                    'cum_price'
                 ]
