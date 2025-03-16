from rest_framework import generics,parsers,status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer,UserSerializer,CustomTokenObtainPairSerializer,ChangePasswordSerializer
from rest_framework.response import Response
from django.db.models import Q
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import IsStuffUser
import os
from django.conf import settings
from transactions.models import Transactions,Budget
from savings.models import Savings
from django.db import transaction
from django.core.cache import cache

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
        user_id=request.user.id
        cache_key = f"user_{user_id}_data"
        cached_data=cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        user=request.user
        serializer=UserSerializer(user)
        user_data = serializer.data

        cache.set(cache_key, user_data, timeout=60 * 60)
        return Response(user_data)

    
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
    

class ChangePasswordView(APIView):
    permission_classes=[IsAuthenticated]

    def post(self,request):
        serializer=ChangePasswordSerializer(data=request.data,context={'request': request})
        if serializer.is_valid():
            user=request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class DeleteCurrentUserView(generics.DestroyAPIView):
    permission_classes=[IsAuthenticated]

    def get_object(self):
        return self.request.user
    
    def delete(self,request,*args,**kwargs):
        user=self.get_object()
        user.delete()
        return Response({"detail": "Your account has been deleted."}, status=status.HTTP_204_NO_CONTENT)
    

class ResetAccountView(APIView):
    permission_classes=[IsAuthenticated]

    def get_object(self):
        return self.request.user
    
    def delete(self,request):
        user=self.get_object()
        
        with transaction.atomic():
            Transactions.objects.filter(user=user).delete()
            Budget.objects.filter(user=user).delete()
            Savings.objects.filter(user=user).delete()
        return Response({"detail": "All user data has been deleted."}, status=status.HTTP_200_OK)
    

class UpdateCurrencyView(APIView):
    permission_classes=[IsAuthenticated]

    def get_object(self):
        return self.request.user
    
    def patch(self,request):
        user=self.get_object()
        new_currency = request.data.get("currency")

        if new_currency not in dict(User.CURRENCY_CHOICES).keys():
            return Response({"error": "Invalid currency."}, status=status.HTTP_400_BAD_REQUEST)
        
        user.currency=new_currency
        user.save()
        return Response({"currency": user.currency}, status=status.HTTP_200_OK)