from django.contrib import admin
from .models import Transactions,Types,Categories

# Register your models here.
admin.site.register(Transactions)
admin.site.register(Types)
admin.site.register(Categories)
