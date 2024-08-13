from rest_framework import serializers
from .models import Savings,Payments


class SavingSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Savings
        fields=['id','name','amount','goal','target_date','status','description','color']


class PaymentsSerializer(serializers.ModelSerializer):

    class Meta:
        model=Payments
        fields=['amount','date','saving']
