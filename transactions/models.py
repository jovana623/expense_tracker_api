from django.db import models
from django.contrib.auth import get_user_model

User=get_user_model()

# Create your models here.
class Categories(models.Model):
    name=models.CharField(max_length=255)
    color=models.CharField(max_length=7)
    

class Types(models.Model):
    name=models.CharField(max_length=255)
    color=models.CharField(max_length=7)
    category=models.ForeignKey(Categories,on_delete=models.CASCADE,default=1)


class Transactions(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,default=2)
    name=models.CharField(max_length=255)
    amount=models.DecimalField(max_digits=10,decimal_places=2)
    date=models.DateField(auto_now_add=True)
    description=models.TextField(default="")
    type=models.ForeignKey(Types,on_delete=models.CASCADE)

    
    

