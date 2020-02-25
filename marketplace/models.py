from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    imagefile= models.ImageField(upload_to='images/')
    phonenumber = models.CharField(max_length=12, null= True)
    major = models.CharField(max_length= 50 ,null= True)
    year = models.CharField(max_length= 4, null= True)


@receiver(post_save, sender=User)
def ensure_profile_exists(sender, **kwargs):
    if kwargs.get('created', False):
        Profile.objects.get_or_create(user=kwargs.get('instance'))

