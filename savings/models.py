from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
import datetime

User=get_user_model()


class Savings(models.Model):

    class TypeStatus(models.TextChoices):
        in_progress='In progress'
        completed='Completed'
        on_hold='On hold' 

    user=models.ForeignKey(User,on_delete=models.CASCADE,default="")
    name=models.CharField(max_length=255)
    amount=models.DecimalField(max_digits=10,decimal_places=2,default=0)
    goal=models.DecimalField(max_digits=10,decimal_places=2)
    target_date=models.DateField()
    started_at=models.DateField(default=datetime.date(2024, 1, 1))
    status=models.CharField(max_length=50,choices=TypeStatus.choices)
    color=models.CharField(max_length=7)
    description=models.TextField()
    

    def __str__(self):
        return self.name


class Payments(models.Model):
    amount=models.DecimalField(max_digits=10,decimal_places=2)
    date=models.DateField(default=datetime.date.today)
    saving=models.ForeignKey(Savings,on_delete=models.CASCADE,default=1,related_name='payments')



@receiver(post_save,sender=Payments)
@receiver(post_delete,sender=Payments)
def update_saving_amount(sender,instance,**kwargs):
    savings=instance.saving
    total_amount=savings.payments.aggregate(total=models.Sum('amount'))['total'] or 0
    savings.amount=total_amount

    if total_amount>=savings.goal:
        new_status=Savings.TypeStatus.completed
    else:
        new_status=Savings.TypeStatus.in_progress

    if savings.status != new_status:
        savings.status = new_status
    savings.save()

       