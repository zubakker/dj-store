from django.contrib.auth.models import User 
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from store.serializers import (UserSerializer, TagSerializer, 
        ProductSerializer, CartSerializer)
from store.models import Tag, Product, Cart
from store.paginators import ProductPaginator

from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.views import APIView

from django.contrib.auth.hashers import check_password
from rest_framework.authtoken.models import Token
from rest_framework import status

from rest_framework.pagination import PageNumberPagination

from django.core.paginator import Paginator


class LoginView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()

    def post(self, request, format=None):
        print(request.data)
        if 'username' not in list(request.data) or 'password' not in list(request.data):
            return Response('No username or password provided',
                            status=status.HTTP_400_BAD_REQUEST)
        user = get_object_or_404(self.queryset, 
                    username=request.data['username'])
        if check_password(request.data['password'], user.password):
            token = Token.objects.get_or_create(user=user)
            content = {
                'token': token[0].key
            }
            return Response(content)
        else:
            return Response('Unauthorized', status=401)

class LogoutView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    def post(self, request, format=None):
        request.user.auth_token.delete()
        return Response({"success": "Successfully logged out."},
                    status=status.HTTP_200_OK)
    

class RegisterView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()

    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = Token.objects.get_or_create(user=user)
            content = {
                'token': token[0].key
            }
            return Response({"success": "Successfully logged out."},
                        status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

class MeView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    def get(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)
    def put(self, request, format=None):
        user_data = UserSerializer(request.user, context={'request': request}).data
        user_data.update(request.data)
        serializer = UserSerializer(request.user, data=user_data, context={'request': request})
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors)
    def delete(self, request, format=None):
        request.user.delete()
        return Response({"success": "Successfully deleted account."},
                    status=status.HTTP_200_OK)

class CartView(APIView):
    # TODO pagination
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart = Cart.objects.get(user=request.user)
        # page = request.GET.get('page')
        # paginator = Paginator(cart, ProductPaginator.page_size)
        # cart.items = paginator.page(page).object_list
        serializer = CartSerializer(cart, context={'request': request})
        return Response(serializer.data)
    def put(self, request):
        cart = Cart.objects.get(user=request.user)
        serializer = CartSerializer(cart, context={'request': request})
        item_id = request.data['id']
        product = Product.objects.get(id=item_id)
        product_ser = ProductSerializer(product, context={'request': request})
        if 'amount' not in list(request.data):
            amount = 1
        else:
            amount = request.data['amount']
        serializer.update(cart, product_ser.data, amount)
        cart.save()
        return Response(serializer.data)
    def delete(self, request):
        item_id = request.GET.get('id')
        amount = request.GET.get('amount')
        cart = Cart.objects.get(user=request.user)
        serializer = CartSerializer(cart, context={'request': request})
        if item_id:
            if not amount:
                amount = 1
            serializer.remove(cart, item_id, amount)
        else:
            serializer.delete(cart)
        cart.save()
        return Response(serializer.data)

class CheckoutView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, format=None):
        cart = Cart.objects.get(user=request.user)
        serializer = CartSerializer(cart, context={'request': request})

        if 'address' not in list(request.data):
            return Response('No address provided',
                            status=status.HTTP_400_BAD_REQUEST)

        address = request.data['address']
        bought_items = serializer.data
        # Send address bought items to shipping #
        serializer.delete(cart)
        cart.save()
        return Response({"success": "Transaction successful."},
                    status=status.HTTP_200_OK)
        
        
    

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def list(self, request):
        list_data = list(request.data)
        queryset = Product.objects.all()
        name = request.GET.get('Name')
        price_higher = request.GET.get('PriceHigher')
        price_lower = request.GET.get('PriceLower')
        stock_greater = request.GET.get('StockGreater')
        tags_list = request.GET.getlist('Tags')

        sort_by = request.GET.get('SortBy')
        
        if name:
            queryset = queryset.filter(name=name)
        if price_higher:
            queryset = queryset.filter(price__gt=price_higher)
        if price_lower:
            queryset = queryset.filter(price__lt=price_lower)
        if stock_greater:
            queryset = queryset.filter(stock__gte=stock_greater)
        for tag in tags_list:
            queryset = queryset.filter(tags=int(tag))

        if sort_by:
            queryset = queryset.order_by(sort_by)
        paginator = ProductPaginator()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = ProductSerializer(result_page, many=True,context={'request': request})

        return paginator.get_paginated_response(serializer.data)



