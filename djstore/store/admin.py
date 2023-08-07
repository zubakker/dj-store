from django.contrib import admin

from store.models import Product, Tag, Cart
# Register your models here.

admin.site.register(Product)
admin.site.register(Tag)
admin.site.register(Cart)
