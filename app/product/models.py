
from django.db import models
from django.conf import settings
# Create your models here.

class Category(models.TextChoices):
    LAPTOP = 'Laptop'
    ELECTRONICS = 'Electronics'
    ART = 'Art'
    FOOD = 'Food'
    HOME = 'Home'
    KITCHEN = 'Kitchen'

class Product(models.Model):
    name = models.CharField(max_length=250, default="", blank=False)
    description = models.TextField(max_length=1000, default="", blank=False)
    price = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    brand = models.CharField(max_length=200 , default="", blank=False)
    category = models.CharField(max_length=70,choices=Category.choices)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    stock = models.IntegerField(default=0)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name