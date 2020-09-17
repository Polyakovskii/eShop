from django.contrib import admin
from .models import Product, Producer, Category, ProductInCart, Cart
# Register your models here.
admin.site.register(Producer)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(ProductInCart)
admin.site.register(Cart)