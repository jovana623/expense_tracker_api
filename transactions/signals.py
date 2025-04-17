from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from savings.models import Payments
from .models import Transactions,Types,Budget
from notifications.models import Notifications
from django.core.cache import cache
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils.timezone import now
from django.db.models import Sum
from django.db import transaction
import traceback

#Create transaction for payment
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


#clear cache on transaction change
@receiver(post_save,sender=Transactions)
def clear_cache_on_transaction_change(sender,instance,**kwargs):
    cache_key_monthly = f"user_{instance.user.id}_monthly_spending_{instance.type.name}"
    cache.delete(cache_key_monthly)
    cache_key_stats=f"user_{instance.user.id}_statistics"
    cache.delete(cache_key_stats)

    if instance.type:
        budget=Budget.objects.filter(user=instance.user,type=instance.type)
        if budget.exists():
            cache_key_budget=f"user_{instance.user.id}_budgets"
            cache.delete(cache_key_budget)
    
    daily_balances_keys = cache.keys(f"daily_balances_{instance.user_id}_*") 
    for key in daily_balances_keys:
        cache.delete(key)

    monthly_balances_keys = cache.keys(f"monthly_balance_{instance.user_id}_*") 
    for key in monthly_balances_keys:
        cache.delete(key)
    

@receiver(post_delete,sender=Transactions)
def clear_cache_on_transaction_delete(sender,instance,**kwargs):
    cache_key_monthly = f"user_{instance.user.id}_monthly_spending_{instance.type.name}"
    cache.delete(cache_key_monthly)
    cache_key_stats=f"user_{instance.user.id}_statistics"
    cache.delete(cache_key_stats)

    if instance.type:
        budget=Budget.objects.filter(user=instance.user,type=instance.type)
        if budget.exists():
            cache_key_budget=f"user_{instance.user.id}_budgets"
            cache.delete(cache_key_budget) 
    
    daily_balances_keys = cache.keys(f"daily_balances_{instance.user_id}_*") 
    for key in daily_balances_keys:
        cache.delete(key)

    monthly_balances_keys = cache.keys(f"monthly_balance_{instance.user_id}_*") 
    for key in monthly_balances_keys:
        cache.delete(key)


#clear cache on budget change
@receiver(post_save,sender=Budget)
def clear_cache_on_budget_change(sender,instance,**kwargs):
    cache_key=f"user_{instance.user.id}_budgets"
    cache.delete(cache_key)

@receiver(post_delete,sender=Budget)
def clear_cache_on_budget_delete(sender,instance,**kwargs):
    cache_key=f"user_{instance.user.id}_budgets"
    cache.delete(cache_key)


#notification create if budget is full
def send_notification(user_id,message):
    channel_layer=get_channel_layer()
    group_name = f"user_{user_id}_notifications"
    current_timestamp = now().strftime("%Y-%m-%d %H:%M:%S")

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type":"send_notification",
            "notification":{
                "text":message,
                "time": current_timestamp
            }
        }
    )
        
def check_budget_and_make_notification(user,type_obj,period):
    now_date=now().date()
    budget=Budget.objects.filter(user=user,type=type_obj,period=period).first()

    if not budget:
        return
    if budget.period=="Monthly":
        transactions=Transactions.objects.filter(
            user=user,
            type=type_obj,
            date__year=now_date.year,
            date__month=now_date.month
        )
        identifier=f"budget:{type_obj.name}:{now_date.year}-{now_date.month:02d}"
    elif budget=="Yearly":
        transactions=Transactions.objects.filter(
            user=user,
            type=type_obj,
            date__year=now_date.year
        )
        identifier=f"budget:{type_obj.name}:{now_date.year}"
    else:
        return

    total=transactions.aggregate(total=Sum('amount'))['total'] or 0

    if total>=budget.amount:
        message = f"Your {str(period).lower()} budget {type_obj.name} is full"
        
        notification_exists=Notifications.objects.filter(user=user,identifier=identifier).exists()

        if not notification_exists:
            Notifications.objects.create(
                user=user,
                message=message,
                identifier=identifier,
                category="budget"
            )
            send_notification(user.id,message) 
    else:  
        deleted_count, _ = Notifications.objects.filter(user=user, identifier=identifier).delete()
        if deleted_count > 0:
            print(">>> Notification deleted, sending WS update")
            if deleted_count > 0:
                send_notification(user.id, {
                    "text": "Budget no longer full – notification removed",
                    "type": "deleted",
                    "identifier": identifier,
                })
            

@receiver(post_save,sender=Transactions)
def handle_transaction_save(sender, instance, created, **kwargs):
        def run_check_monthly():
            check_budget_and_make_notification(instance.user, instance.type, period="Monthly")

        def run_check_yearly():
            check_budget_and_make_notification(instance.user, instance.type, period="Yearly")

        transaction.on_commit(run_check_monthly)
        transaction.on_commit(run_check_yearly)
        

@receiver(post_delete,sender=Transactions)
def handle_transaction_delete(sender, instance, **kwargs):
        def run_check_monthly_del():
            check_budget_and_make_notification(instance.user, instance.type, period="Monthly")

        def run_check_yearly_del():
            check_budget_and_make_notification(instance.user, instance.type, period="Yearly")
        
        transaction.on_commit(run_check_monthly_del)
        transaction.on_commit(run_check_yearly_del)
        