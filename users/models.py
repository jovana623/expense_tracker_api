from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self,email,password=None,**extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

 
class User(AbstractBaseUser,PermissionsMixin): 
    CURRENCY_CHOICES = [
        ("EUR", "Euro (€)"),
        ("USD", "US Dollar ($)"),
        ("GBP", "British Pound (£)"),
        ("JPY", "Japanese Yen (¥)"),
        ("AUD", "Australian Dollar (A$)"),
        ("CAD", "Canadian Dollar (C$)"),
        ("CHF", "Swiss Franc (CHF)"),
        ("CNY", "Chinese Yuan (¥)"),
        ("SEK", "Swedish Krona (kr)"),
        ("NZD", "New Zealand Dollar (NZ$)"), 
    ]
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    avatar = models.ImageField(upload_to="avatars/",blank=True,null=True)
    last_login = models.DateTimeField(null=True, blank=True) 
    currency=models.CharField(max_length=3,choices=CURRENCY_CHOICES,default="EUR") 

    objects=UserManager()
 
    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['username']
 