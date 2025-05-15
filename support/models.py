from django.db import models
from django.conf import settings
from django.utils import timezone

class SupportThread(models.Model):
    
    class ThreadStatus(models.TextChoices):
        OPEN="open","Open"
        IN_PROGRESS="in_progress","In Progress"
        CLOSED="closed","Closed"

    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="support_thread")
    staff=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="assigned_threads")
    status=models.CharField(max_length=100,choices=ThreadStatus.choices)
    subject=models.CharField(max_length=250)
    archived=models.BooleanField(default=False)
    last_message=models.ForeignKey('SupportMessage',on_delete=models.SET_NULL,null=True,blank=True,related_name='+')
    user_last_read_at=models.DateTimeField(null=True,blank=True)
    staff_last_read_at=models.DateTimeField(null=True,blank=True)

    def __str__(self):
        return self.subject


class SupportMessage(models.Model):
    thread=models.ForeignKey(SupportThread,on_delete=models.CASCADE,related_name="messages")
    sender=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    message=models.TextField()
    sent_at=models.DateTimeField(default=timezone.now,db_index=True)

    def save(self,*args,**kwargs):
        is_new=self._state.adding
        super().save(*args,**kwargs)
        if is_new and self.thread:
            self.thread.last_message=self
            self.thread.save(update_fields=['last_message'])

    def __str__(self):
        return f"Msg by {self.sender.username} in thread {self.thread.id}"