from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from savings.models import Payments
from .models import Transactions,Types,Budget
from django.core.cache import cache

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
    

#clear cache on budget change
@receiver(post_save,sender=Budget)
def clear_cache_on_budget_change(sender,instance,**kwargs):
    cache_key=f"user_{instance.user.id}_budgets"
    cache.delete(cache_key)

@receiver(post_delete,sender=Budget)
def clear_cache_on_budget_delete(sender,instance,**kwargs):
    cache_key=f"user_{instance.user.id}_budgets"
    cache.delete(cache_key)