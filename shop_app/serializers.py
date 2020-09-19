from rest_framework import serializers
from .models import Product, Cart, ProductInCart, Order
import datetime
from django.db.models import F, Sum, FloatField


class ListProductSerializer(serializers.ModelSerializer):

    category = serializers.SlugRelatedField(slug_field='name', read_only=True)
    producer = serializers.SlugRelatedField(slug_field='name', read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'category', 'producer', 'price')


class SingleProductSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field='name', read_only=True)
    producer = serializers.SlugRelatedField(slug_field='name', read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'category', 'producer', 'description', 'price', 'created')


class CreateProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ('id', 'name', 'category', 'producer', 'description', 'price', 'created')


class CreateProductInCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductInCart
        fields = ('id', 'product', 'count', )

    def create(self, validated_data):
        product = ProductInCart.objects.create(
            product=validated_data['product'],
            count=validated_data['count']
        )
        return product


class UpdateProductInCartSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField()

    class Meta:
        model = ProductInCart
        fields = ('id', 'product', 'count', )


class CartSerializer(serializers.ModelSerializer):

    products = UpdateProductInCartSerializer(many=True)

    class Meta:
        model = Cart
        fields = ('id', 'user', 'products', 'total_price')


class ListOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class CreateOrderSerializer(serializers.ModelSerializer):
    date_of_delivery = serializers.DateField()

    class Meta:
        model = Order
        fields = ('date_of_delivery', )

    def create(self, request, validated_data):
        #TODO rework this
        cart = Cart.objects.annotate(
            total_price=(Sum(F('products__count') * F('products__product__price'), output_field=FloatField()))
        ).get(user=request.user)
        order = Order.objects.create(date_of_delivery=validated_data['date_of_delivery'], user=request.user, date_of_creation=datetime.datetime.now(), total_price=cart.total_price)
        for product in cart.products.all():
            order.products.add(product)
        order.save()
        cart.clear()
        cart.save()
        return order