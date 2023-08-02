from django.db import models

from django.contrib.auth.models import User

# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=31)
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=127)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(max_length=1023)
    vendor_code = models.CharField(max_length=16)
    stock = models.IntegerField()

    tags = models.ManyToManyField(Tag)

    author = models.ForeignKey(
            User,
            models.SET_NULL,
            blank=True,
            null=True)

    def __str__(self):
        return self.name

