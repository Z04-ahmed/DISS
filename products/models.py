from django.db import models
from accounts.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100)
    website = models.URLField()
    is_approved = models.BooleanField(default=False)
    def __str__(self):
        return self.name

class Product(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    wishlist_users = models.ManyToManyField(User, related_name='wishlist')
    is_trending = models.BooleanField(default=False)


class BrandRepresentative(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    last_login = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username
