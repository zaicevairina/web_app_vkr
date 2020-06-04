from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
	nick = models.CharField('ник', max_length=128, default='user')
	avatar = models.ImageField('аватар', upload_to='images/', null=True)

