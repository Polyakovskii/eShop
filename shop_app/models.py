from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Producer(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):

    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    producer = models.ForeignKey(Producer, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    price = models.FloatField()

    def __str__(self):
        return self.name


class ProductInCart(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=1)


class Cart(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(ProductInCart)

    @property
    def total_price(self):
        total_price = 0
        for product in self.products.all():
            total_price += product.product.price * product.count
        return total_price

    def clear(self):
        self.products.clear()
        self.save()

    def add_product(self, product: ProductInCart):
        self.products.add(product)

    def is_empty(self):
        if self.products.all().exists():
            return False
        else:
            return True


class Order(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(ProductInCart)
    date_of_creation = models.DateField(auto_created=True)
    is_paid = models.BooleanField(default=False)
    date_of_delivery = models.DateTimeField()
    total_price = models.FloatField()