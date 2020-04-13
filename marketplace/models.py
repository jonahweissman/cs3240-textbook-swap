from django.db import models
from django.contrib.auth.models import User
from phone_field import PhoneField
from django_auto_one_to_one import AutoOneToOneModel
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.validators import MinValueValidator
import uuid
import os
# Create your models here.

class Profile(AutoOneToOneModel(User)):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, default= uuid)
    imagefile = models.ImageField(upload_to='images/', null=True, blank=True)
    phonenumber = PhoneField(null=True, blank=True)
    major = models.CharField(max_length=50, null=True, blank=True)
    year = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

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
        if not old_file.name == '' and os.path.isfile(old_file.path):
            os.remove(old_file.path)


class Item(models.Model):
    item_condition_choices = (("Like New", "Like New"),("Good", "Good"), ("Fair", "Fair"), ("Poor", "Poor"))
    item_name = models.CharField(max_length=100, null=True)
    item_isbn = models.CharField(max_length=100, null=True)
    item_edition = models.IntegerField(null=True)
    item_author = models.CharField(max_length=100, null=True)
    item_course = models.CharField(max_length=100, null=True)
    item_price = models.IntegerField(null=True)
    item_image = models.ImageField(upload_to='images/', null=True)
    item_condition = models.CharField(max_length=20, choices=item_condition_choices, default= "Brand New")
    item_posted_date = models.DateField(null=True)
    item_seller_name = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    item_description = models.TextField(max_length= 1000, null=True)

    def __str__(self):
        return self.item_name


class Conversation(models.Model):
    buyer = models.ForeignKey(Profile, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.buyer} interested in {self.item}'

class Message(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    in_response_to = models.OneToOneField('self', on_delete=models.CASCADE, null=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)

    def __str__(self):
        return self.text
