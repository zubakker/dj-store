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

class Cart(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    items = models.JSONField(blank=True, default=list)
    cum_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    def __str__(self):
        return self.user.username
    def __len__(self):
        return len(self.items)
    def __getitem__(self, key):
        return self.items[key]
