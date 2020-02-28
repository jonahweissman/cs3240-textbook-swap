from django.db import models
from django.contrib.auth.models import User
from django_auto_one_to_one import AutoOneToOneModel

# Create your models here.

class Profile(AutoOneToOneModel(User)):
    user_ratings = models.IntegerField(default= 5)

class Item(models.Model):
    item_condition_choices = (("Like New", "Like New"),("Good", "Good"), ("Fair", "Fair"), ("Poor", "Poor"))
    item_name = models.CharField(max_length=100)
    item_price = models.IntegerField()
    item_condition = models.CharField(max_length=20, choices=item_condition_choices, default= "Brand New")
    item_posted_date = models.DateField()
    item_seller_name = models.ForeignKey(Profile, on_delete=models.CASCADE)
    item_description = models.TextField(max_length= 1000)

    def __str__(self):
        return self.item_name




