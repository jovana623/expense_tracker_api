from django.db import models
from django.contrib.auth import get_user_model
import datetime

User=get_user_model()


class Savings(models.Model):

    class TypeStatus(models.TextChoices):
        in_progress='In progress'
        completed='Completed'
        on_hold='On hold'

    user=models.ForeignKey(User,on_delete=models.CASCADE,default=2)
    name=models.CharField(max_length=255)
    amount=models.DecimalField(max_digits=10,decimal_places=2,default=0)
    goal=models.DecimalField(max_digits=10,decimal_places=2)
    target_date=models.DateField()
    status=models.CharField(max_length=50,choices=TypeStatus.choices)
    color=models.CharField(max_length=7)
    description=models.TextField()

    def __str__(self):
        return self.name


class Payments(models.Model):
    amount=models.DecimalField(max_digits=10,decimal_places=2)
    date=models.DateField(default=datetime.date.today)
    saving=models.ForeignKey(Savings,on_delete=models.CASCADE,default=1)

    