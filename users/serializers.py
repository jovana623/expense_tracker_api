from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User=get_user_model()

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'avatar', 'is_staff', 'is_superuser', 'is_active', 'created_at','last_login']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model=User
        fields=['id','email','username','password'] 

    def create(self,validated_data):
        user=User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user
    

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token= super().get_token(user)
        token['email']=user.email
        return token
    

class ChangePasswordSerializer(serializers.Serializer):
    old_password=serializers.CharField(write_only=True)
    new_password=serializers.CharField(write_only=True)
    confirm_password=serializers.CharField(write_only=True)

    def validate(self, data):
        if data["new_password"]!=data["confirm_password"]:
            raise serializers.ValidationError({"confirm_password":"Passwords must match"})
        return data
    
    def validate_old_password(self,value):
        user=self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value