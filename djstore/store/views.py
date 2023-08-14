from django.contrib.auth.models import User 
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from store.serializers import (UserSerializer, TagSerializer, 
        ProductSerializer, CartSerializer, CartItemSerializer, TokenSerializer,
        UserAuthSerializer, UserUpdateSerializer)
from store.models import Tag, Product, Cart
from store.paginators import ProductPaginator
from store.filters import ProductTagsFilterSet

from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.views import APIView

from django.contrib.auth.hashers import check_password
from rest_framework.authtoken.models import Token
from rest_framework import status

from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from rest_framework.schemas import AutoSchema

from rest_framework.filters import OrderingFilter 

from django.core.paginator import Paginator

from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi



class LoginView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()

    @swagger_auto_schema(responses={200: TokenSerializer,
                                    400: 'No username or password provided',
                                    401: 'Invalid password',
                                    404: 'Invalid username'},
                         request_body=UserAuthSerializer)
    def post(self, request, format=None):
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
    @swagger_auto_schema(responses={200: 'Successfully logged out'})
    def post(self, request, format=None):
        request.user.auth_token.delete()
        return Response({"success": "Successfully logged out."},
                    status=status.HTTP_200_OK)
    

class RegisterView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()

    @swagger_auto_schema(responses={200: TokenSerializer,
                                    400: 'Invalid username or password'},
                         request_body=UserAuthSerializer)
    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = Token.objects.get_or_create(user=user)
            content = {
                'token': token[0].key
            }
            return Response(content)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

class MeView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    @swagger_auto_schema(responses={200: UserSerializer})
    def get(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    @swagger_auto_schema(responses={200: UserSerializer}, 
                         request_body=UserUpdateSerializer)
    def put(self, request, format=None):
        user_data = UserSerializer(request.user, context={'request': request}).data
        user_data.update(request.data)
        serializer = UserSerializer(request.user, data=user_data, context={'request': request})
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors)

    @swagger_auto_schema(responses={200: "Successfully deleted account"})
    def delete(self, request, format=None):
        request.user.delete()
        return Response({"success": "Successfully deleted account."},
                    status=status.HTTP_200_OK)

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    product_id = openapi.Parameter('id', openapi.IN_QUERY, description="Id of a product to be deleted from cart", type=openapi.TYPE_INTEGER)
    product_amount  = openapi.Parameter('amount', openapi.IN_QUERY, description="Amount of products to be deleted from cart", type=openapi.TYPE_INTEGER)


    def list(self, request):
        # queryset = self.filter_queryset(self.get_queryset())
        cart = Cart.objects.get(user=request.user)
        # page = request.GET.get('page')
        # paginator = Paginator(cart, ProductPaginator.page_size)
        # cart.items = paginator.page(page).object_list
        serializer = CartSerializer(cart, context={'request': request})
        return Response(serializer.data)
    @swagger_auto_schema(request_body=CartItemSerializer, responses={200: CartSerializer})
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
    @swagger_auto_schema(responses={200: CartSerializer}, manual_parameters=[
        product_id, product_amount
    ])
    
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

    shipment_address = openapi.Parameter('address', openapi.IN_QUERY, description="Shipment address for delivery of bought products", type=openapi.TYPE_STRING)
    @swagger_auto_schema(responses={200: 'Transaction successful',
                                    400: 'No address provided'}, 
                         manual_parameters=[shipment_address])
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
        
        

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    paginator = ProductPaginator()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ProductTagsFilterSet


    
    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        paginator = ProductPaginator()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = ProductSerializer(result_page, many=True,context={'request': request})

        return paginator.get_paginated_response(serializer.data)



