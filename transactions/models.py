from django.db import models
from django.contrib.auth import get_user_model
import datetime

User=get_user_model()

class Categories(models.Model):
    name=models.CharField(max_length=255)
    color=models.CharField(max_length=7)

    def __str__(self):
        return self.name
    

class Types(models.Model):
    name=models.CharField(max_length=255)
    color=models.CharField(max_length=7)
    category=models.ForeignKey(Categories,on_delete=models.CASCADE,default=1)

    def __str__(self):
        return self.name


class Transactions(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,default=2)
    name=models.CharField(max_length=255)
    amount=models.DecimalField(max_digits=10,decimal_places=2)
    date=models.DateField(default=datetime.date.today)
    description=models.TextField(default="")
    type=models.ForeignKey(Types,on_delete=models.CASCADE)






    
    

