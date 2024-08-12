from rest_framework import serializers
from .models import Categories,Types,Transactions


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model=Categories
        fields=['id','name','color']


class TypeSerializer(serializers.ModelSerializer):

    class Meta:
        model=Types
        fields=['id','name','color','category']


class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model=Transactions
        fields=['id','name','date','amount','type','description']