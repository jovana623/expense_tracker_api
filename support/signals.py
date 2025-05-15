from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SupportMessage
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

User=get_user_model()
@receiver(post_save,sender=SupportMessage)
def support_message_saved(sender,instance,created,**kwargs):
    if created:
        message=instance
        thread=message.thread
        sender_user=message.sender

        participants_to_notify = set()

        if thread.user:
            participants_to_notify.add(thread.user)
        if thread.staff:
            participants_to_notify.add(thread.staff)
        
        if not participants_to_notify:
            print(f"New message in thread {thread.id}, but no recipients to notify.")
            return
        
        channel_layer=get_channel_layer()

        message_payload={
            'type':'invalidate_threads',
            'thread_id':str(thread.id), 
        }

        print(f"New message in thread {thread.id}. Sending notification to recipients: {[r.username for r in participants_to_notify]}")

        for recipient in participants_to_notify:
            recipient_group_name=f"user_{recipient.id}"
            try:
                async_to_sync(channel_layer.group_send)(
                    recipient_group_name,
                    message_payload
                )
                print(f"Notification sent to group {recipient_group_name}")
            except Exception as e:
                print(f"Failed to send notification to group {recipient_group_name}: {e}")
