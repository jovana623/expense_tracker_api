from rest_framework import generics,parsers,status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer,UserSerializer,CustomTokenObtainPairSerializer
from rest_framework.response import Response
from django.db.models import Q
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import IsStuffUser
import os
from django.conf import settings

User=get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset=User.objects.all()
    serializer_class=RegisterSerializer
    permission_class=[AllowAny] 
    

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class=CustomTokenObtainPairSerializer
    

class LogoutView(APIView): 
    permission_classes=[IsAuthenticated]

    def post(self,request): 
        try:
            refresh_token=request.data["refresh"]
            token=RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"}, status=200)
        except Exception as e:
             return Response({"error": "Invalid token"}, status=400)
    

class CurrentUserView(APIView):
    permission_classes=[IsAuthenticated]
    parser_classes=[parsers.MultiPartParser,parsers.FormParser]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    def patch(self,request):
        user=request.user
        data = request.data.copy()

        if 'avatar' in request.FILES:
            if user.avatar and os.path.isfile(user.avatar.path):
                os.remove(user.avatar.path) 
            user.avatar = request.FILES['avatar'] 
        if 'username' in data:
            user.username=data['username']
    
        user.save()
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserListAPIView(generics.ListAPIView):
    serializer_class=UserSerializer
    permission_classes=[IsStuffUser]
    

    def get_queryset(self):
        queryset=User.objects.all()
        search=self.request.query_params.get('search')

        if search:
            queryset=queryset.filter(Q(username__icontains=search) | Q(email__icontains=search))
        
        return queryset

class RetrieveUpdateDestroyUserAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset=User.objects.all()
    serializer_class=UserSerializer
    permission_classes=[IsStuffUser]  
    