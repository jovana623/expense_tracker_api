from django.db import models
from django.contrib.auth import get_user_model

User=get_user_model()

class Notifications(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="notifications")
    category=models.CharField(max_length=100,null=True,blank=True)
    identifier=models.CharField(max_length=255,null=True,blank=True)
    message=models.TextField(blank=True)
    is_read=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering=["-created_at"]