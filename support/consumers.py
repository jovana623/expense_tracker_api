from django.contrib.auth import get_user_model
from channels.generic.websocket import AsyncJsonWebsocketConsumer,WebsocketConsumer
from .models import SupportThread,SupportMessage
from channels.db import database_sync_to_async
import json
from .serializers import SupportMessageSerializer
from asgiref.sync import async_to_sync
from django.utils import timezone

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.thread_id=self.scope['url_route']['kwargs']['thread_id']
        self.room_group_name=f'chat_{self.thread_id}'

        self.user=self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return
        
        try:
            self.thread=await self.get_thread(self.thread_id)
            if self.thread is None:
                await self.close()
                return
            
            is_authorized=(
                self.user==self.thread.user or
                self.user==self.thread.staff or
                (self.user.is_staff and self.thread.status!=SupportThread.ThreadStatus.CLOSED)
            )

            if not is_authorized:
                await self.close()
                return
            
            await self.update_thread_read_time(self.user,self.thread)
              
        except Exception as e:
            print(f"Error during connect authorization: {e}") 
            await self.close()
            return
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        print(f"User {self.user.username} connected to thread {self.thread_id}")

    async def disconnect(self, code):
        if hasattr(self,'room_group_name') and hasattr(self,'channel_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        try:
            text_data_json=json.loads(text_data)
            message_content=text_data_json['message']
        except(json.JSONDecodeError,KeyError):
            await self.send(text_data=json.dumps({'error':'Invalid message format.'}))
            return
        
        if(self.user!=self.thread.user and self.user!=self.thread.staff) or \
        self.thread.status!=SupportThread.ThreadStatus.IN_PROGRESS:
            await self.send(text_data=json.dumps({'error':'You are not allowed to send message in this thread'}))
            return
        
        try:
            message=await self.create_message(message_content)
            serializer=SupportMessageSerializer(message)
            message_data=serializer.data

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type':'chat_message',
                    'message':message_data
                }
            )

        except Exception as e:
            await self.send(text_data=json.dumps({'error':'Failed to process message'}))
    
    async def chat_message(self,event):
        message_data=event['message']
        await self.send(text_data=json.dumps(message_data))

    @database_sync_to_async
    def get_thread(self,thread_id):
        try:
            return SupportThread.objects.select_related('user','staff').get(id=thread_id)
        except SupportThread.DoesNotExist:
            return None
    
    @database_sync_to_async
    def create_message(self,message_content):
        message=SupportMessage.objects.create(
            thread=self.thread,
            sender=self.user,
            message=message_content
        )
        self.thread.last_message = message
        self.thread.save(update_fields=["last_message"])
        return message

    
    @database_sync_to_async
    def update_thread_read_time(self,user_obj,thread_obj):
        if not(user_obj and user_obj.is_authenticated and thread_obj):
            return False
        
        now=timezone.now()
        updated_fields=[]
        changed=False

        if thread_obj.user==user_obj:
            if thread_obj.user_last_read_at is None or now>thread_obj.user_last_read_at:
                thread_obj.user_last_read_at=now
                updated_fields.append('user_last_read_at')
                changed=True
        elif thread_obj.staff==user_obj:
            if thread_obj.staff_last_read_at is None or now>thread_obj.staff_last_read_at:
                thread_obj.staff_last_read_at=now
                updated_fields.append('staff_last_read_at')
                changed=True

        if changed:
            thread_obj.save(update_fields=updated_fields)
            return True
        return False


class MessageNotificationConsumer(WebsocketConsumer):
    def connect(self):
        user=self.scope["user"]
        if user:
            self.user=user
            self.user_group_name=f"user_{self.user.id}"

            async_to_sync(self.channel_layer.group_add)(
                self.user_group_name,
                self.channel_name
            )
            self.accept()
        else:
            self.close()

    def disconnect(self, code):
        if hasattr(self,'user_group_name'):
            async_to_sync(self.channel_layer.group_discard)(
               self.user_group_name,
               self.channel_name 
            )
        else:
            print("Anonymous connection closed.")

    def invalidate_threads(self,event):
        self.send(text_data=json.dumps({
            'type': event['type'],
        }))
        