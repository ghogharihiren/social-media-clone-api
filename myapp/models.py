from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    
    email=models.EmailField(unique=True)
    mobile=models.CharField(max_length=15,null=True,blank=True)
    profile_pic=models.FileField(upload_to='profile',default='1.png')
    bio=models.TextField(max_length=200,null=True,blank=True)
    followers = models.ManyToManyField('User',related_name='follower')
    following = models.ManyToManyField('User',related_name='followings')
    
    def __str__(self):
        return self.email
    
class UserToken(models.Model):
    user = models.ForeignKey(User, related_name="user", on_delete=models.CASCADE)
    token = models.CharField(null=True, max_length=500)
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)

    def __str__(self):
        return str(self.user)