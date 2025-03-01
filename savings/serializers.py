from rest_framework import serializers
from .models import Savings,Payments

class PaymentsSerializer(serializers.ModelSerializer):

    class Meta:
        model=Payments
        fields=['id','amount','date','saving']


class SavingSerializer(serializers.ModelSerializer):
    payments=PaymentsSerializer(many=True,read_only=True)
    
    class Meta:
        model=Savings
        fields=['id','name','amount','goal','target_date','started_at','status','description','color','payments']

        read_only_fields = ['id', 'amount', 'payments']


