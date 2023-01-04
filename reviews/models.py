from django.db import models
from products.models import Products
# Create your models here.
#Review
class Review(models.Model):
    product = models.ForeignKey(Products,on_delete=models.CASCADE)
    uname = models.CharField(max_length=100, blank=True)
    email = models.CharField(max_length=150, null=False)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    status = models.BooleanField(default=True)
    ip = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.uname