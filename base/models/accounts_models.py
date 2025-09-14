from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomerUser(AbstractUser):
    GENDER_CHOICES = [
        ('M', '男性'),
        ('F', '女性'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    is_premium = models.BooleanField(default=False)

    def __str__(self):
        return self.username