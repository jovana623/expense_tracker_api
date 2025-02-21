from rest_framework import generics
from rest_framework.views import APIView
from django.contrib.auth import login,logout
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer,UserSerializer,CustomTokenObtainPairSerializer
from rest_framework.response import Response
from django.db.models import Q
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import IsStuffUser

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

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)


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