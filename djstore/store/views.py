from django.contrib.auth.models import User 
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from store.serializers import (UserSerializer, TagSerializer, ProductSerializer)
from store.models import Tag, Product
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.views import APIView

from django.contrib.auth.hashers import check_password
from rest_framework.authtoken.models import Token
from rest_framework import status

class LoginView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()

    def post(self, request, format=None):
        if 'username' not in list(request.data) or 'password' not in list(request.data):
            return Response('Bad request',
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
            return Response({"success": "Successfully edited account information."},
                        status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors)
    def delete(self, request, format=None):
        request.user.delete()
        return Response({"success": "Successfully deleted account."},
                    status=status.HTTP_200_OK)

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
