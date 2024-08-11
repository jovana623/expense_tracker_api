from rest_framework import generics
from rest_framework.views import APIView
from django.contrib.auth import login,logout
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer,LoginSerializer
from rest_framework.response import Response
from rest_framework import status

User=get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset=User.objects.all()
    serializer_class=RegisterSerializer
    permission_class=[AllowAny] 


class LoginView(APIView):
    serializer_class=LoginSerializer
    permission_classes=[AllowAny]

    def post(self,request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=serializer.validated_data['user']

        login(request,user)

        return Response({
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username
            }
        })
    

class LogoutView(APIView):
    permission_classes=[IsAuthenticated]

    def post(self,request):
        logout(request)
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)