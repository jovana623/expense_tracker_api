from django.db import models
from django.contrib.auth import get_user_model
import datetime
from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from savings.models import Payments
 
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
    user=models.ForeignKey(User,on_delete=models.CASCADE,default="")
    name=models.CharField(max_length=255)
    amount=models.DecimalField(max_digits=10,decimal_places=2)
    date=models.DateField(default=datetime.date.today)
    description=models.TextField(default="")
    type=models.ForeignKey(Types,on_delete=models.CASCADE)


class Budget(models.Model):
 
    class Period(models.TextChoices):
        monthly='Monthly' 
        yearly="Yearly"

    user=models.ForeignKey(User,on_delete=models.CASCADE,default="")
    type=models.ForeignKey(Types,on_delete=models.CASCADE)
    amount=models.DecimalField(max_digits=10,decimal_places=2)
    date=models.DateField(default=datetime.date.today)
    period=models.CharField(max_length=10,choices=Period.choices)

    def __str__(self):
        return f"{self.user} - {self.type.name} - {self.period}"
    
 
@receiver(post_save,sender=Payments)
def create_transaction_for_payments(sender,instance,**kwargs):
    saving=instance.saving
    transaction_type=Types.objects.filter(name="Savings").first()

    Transactions.objects.create(
        user=saving.user,
        name=f"Payment for {saving.name}",
        amount=instance.amount,
        date=instance.date,
        description=f"Payment toward saving goal {saving.name}",
        type=transaction_type
    )

@receiver(post_delete,sender=Payments)
def delete_transaction_for_payments(sender,instance,**kwargs):
    saving=instance.saving
    
    Transactions.objects.filter(
        user=saving.user,
        name=f"Payment for {saving.name}",
        amount=instance.amount,
        date=instance.date,
        description=f"Payment toward saving goal {saving.name}",
    ).delete()


    