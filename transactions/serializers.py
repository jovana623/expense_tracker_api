from rest_framework import serializers
from .models import Categories,Types,Transactions,Budget


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model=Categories
        fields=['id','name','color']


class TypeSerializer(serializers.ModelSerializer):
    category=serializers.PrimaryKeyRelatedField(queryset=Categories.objects.all())
    
    class Meta:
        model=Types
        fields=['id','name','color','category']


class TypeReadSerializer(serializers.ModelSerializer):
    category=CategorySerializer()

    class Meta:
        model=Types
        fields=['id','name','color','category']



class TransactionSerializer(serializers.ModelSerializer):
    type = serializers.PrimaryKeyRelatedField(queryset=Types.objects.all())

    class Meta:
        model=Transactions
        fields=['id','name','date','amount','type','description']


class TransactionReadSerializer(serializers.ModelSerializer):
    type=TypeReadSerializer()
 
    class Meta:
        model=Transactions
        fields=['id','name','date','amount','type','description','user']


class BudgetSerializer(serializers.ModelSerializer):

    class Meta:
        model=Budget
        fields=['id','type','amount','date','period','user'] 


class BudgetReadSerializer(serializers.ModelSerializer):
    type=TypeReadSerializer()

    class Meta: 
        model=Budget
        fields=['id','type','amount','date','period','user'] 