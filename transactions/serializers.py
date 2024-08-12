from rest_framework import serializers
from .models import Categories,Types


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model=Categories
        fields=['id','name','color']


class TypeSerializer(serializers.ModelSerializer):

    class Meta:
        model=Types
        fields=['id','name','color','category']
