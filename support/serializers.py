from .models import SupportThread,SupportMessage
from django.contrib.auth import get_user_model
from rest_framework import serializers
from users.serializers import SimpleUserSerializer
from django.utils import timezone

User=get_user_model()

class SupportMessageSerializer(serializers.ModelSerializer):
    sender=serializers.CharField(source='sender.username', read_only=True)
    sent_at=serializers.DateTimeField(read_only=True)

    class Meta:
        model=SupportMessage
        fields=['id','thread','sender','message','sent_at']


class SupportThreadSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    staff = serializers.CharField(source='staff.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    other_user=serializers.SerializerMethodField()
    last_message=serializers.SerializerMethodField()
    has_unread=serializers.SerializerMethodField()

    class Meta:
        model=SupportThread
        fields=['id','user','staff','subject','status','status_display','archived','other_user','last_message','has_unread']
        read_only_fields=['id','user','staff','messages','status_display','last_message','has_unread']

    def get_other_user(self,obj):
        request=self.context.get('request')

        if not request:
            return None
        
        current_user=request.user
        if obj.user==current_user and obj.staff:
            return SimpleUserSerializer(obj.staff).data
        elif obj.staff==current_user:
            return SimpleUserSerializer(obj.user).data
        elif obj.staff is None and current_user.is_staff:
            return SimpleUserSerializer(obj.user).data
        return None
    
    def get_last_message(self,obj):
        if obj.last_message:
            return SupportMessageSerializer(obj.last_message).data
        return None
    
    def get_has_unread(self,obj):
        request=self.context.get('request')
        if not request and not hasattr(request,'user'):
            return None
        
        current_user=request.user
        final_message_time=obj.last_message.sent_at if obj.last_message else None
        if final_message_time is None:
            return False
        
        user_specific_last_read_time=None

        if obj.user==current_user:
            user_specific_last_read_time=obj.user_last_read_at
        elif obj.staff==current_user:
            user_specific_last_read_time=obj.staff_last_read_at
        else:
            return False
        
        if user_specific_last_read_time is None:
            return True
        
        try:
            if timezone.is_naive(final_message_time):final_message_time=timezone.make_aware(final_message_time)
            if timezone.is_naive(user_specific_last_read_time):user_specific_last_read_time=timezone.make_aware(user_specific_last_read_time)
            is_unread=final_message_time>user_specific_last_read_time
            return is_unread
        except TypeError as e:
            return False

    
class CreateSupportThreadAndMessageSerializer(serializers.Serializer):
    subject=serializers.CharField(max_length=250,min_length=3)
    message=serializers.CharField(min_length=10,trim_whitespace=False)