from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import os

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

@receiver(models.signals.pre_save, sender=Profile)
def auto_delete_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = sender.objects.get(pk=instance.pk).imagefile
    except sender.DoesNotExist:
        return False

    new_file = instance.imagefile
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)