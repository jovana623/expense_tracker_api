from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth import authenticate

User=get_user_model()

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=User
        fields=['id','name','username','avatar','is_staff','is_active']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model=User
        fields=['email','username','password']

    def create(self,validated_data):
        user=User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user
    

class LoginSerializer(serializers.Serializer):
    email=serializers.EmailField()
    password=serializers.CharField(write_only=True)

    def validate(self,data):
        email=data.get('email',None)
        password=data.get('password',None)
        user=authenticate(email=email,password=password)

        if user is None:
            raise serializers.ValidationError('Invalid email or password')
        
        data['user']=user
        return data