from django.db import models
from django.contrib.auth import get_user_model

User=get_user_model()

# Create your models here.
class Savings(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,default=2)
    name=models.CharField(max_length=255)
    amount=models.DecimalField(max_digits=10,decimal_places=2)
    goal=models.DecimalField(max_digits=10,decimal_places=2)
    target_date=models.DateField()
    status=models.CharField(max_length=50)
    color=models.CharField(max_length=7)
    description=models.TextField()


class Payments(models.Model):
    amount=models.DecimalField(max_digits=10,decimal_places=2)
    date=models.DateField(auto_now_add=True)
    saving=models.ForeignKey(Savings,on_delete=models.CASCADE,default=1)