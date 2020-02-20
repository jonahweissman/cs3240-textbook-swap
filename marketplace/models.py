from django.db import models

# Create your models here.

class User(models.Model):
    
    #ratings_choices= ((1,1), (2,2), (3,3), (4,4), (5,5))
    user_name= models.CharField(max_length= 100)
    user_email = models.EmailField()
    user_ratings = models.IntegerField()
    def __str__(self):
        return self.user_name
class Item(models.Model):
    item_condition_choices = (("Brand New", "Brand New"), ("Used", "Used") )
    item_name = models.CharField(max_length=100)
    item_price = models.IntegerField()
    item_condition = models.CharField(max_length=20, choices=item_condition_choices)
    item_posted_date = models.DateField()
    item_seller_name = models.ForeignKey(User, on_delete=models.CASCADE)
    item_description = models.TextField(max_length= 1000)
    def __str__(self):
        return self.item_name





