from django.db.models import F, Sum, FloatField
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Product, Cart, Order
from .serializers import ListProductSerializer, SingleProductSerializer, CreateProductSerializer, CartSerializer, ProductInCartSerializer, ListOrderSerializer, CreateOrderSerializer
from .filters import ProductFilter
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import IsAdminOrReadOnly
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
# Create your views here.

class ProductView(viewsets.GenericViewSet,
                  viewsets.mixins.ListModelMixin,
                  viewsets.mixins.RetrieveModelMixin,
                  viewsets.mixins.CreateModelMixin):
    queryset = Product.objects.all()
    filter_backends = (DjangoFilterBackend, )
    filter_class = ProductFilter
    permission_classes = (IsAdminOrReadOnly, )

    def get_serializer_class(self):
        if self.action == 'list':
            return ListProductSerializer
        if self.action == 'retrieve':
            return SingleProductSerializer
        if self.action == 'create':
            return CreateProductSerializer


class CartView(APIView):
    permission_classes = (permissions.IsAuthenticated, )
    def get(self, request):
        try:
            cart = Cart.objects.annotate(
                total_price=(Sum(F('products__count') * F('products__product__price'), output_field=FloatField()))
            ).get(user=request.user)
            return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            cart = Cart.objects.create(user=request.user)
            return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)


    def post(self, request):
        serializer = ProductInCartSerializer(data= request.data)
        if serializer.is_valid():
            cart = Cart.objects.get(user=request.user)
            if cart is None:
                cart = Cart.objects.create(user=request.user)
            try:
                product = cart.products.get(product=serializer.validated_data['product'])
            except ObjectDoesNotExist:
                product = serializer.create(serializer.validated_data)
                cart.products.add(product)
                return Response(status=status.HTTP_201_CREATED)
            else:
                product.count = product.count + serializer.validated_data['count']
                product.save()
                return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status.HTTP_400_BAD_REQUEST)


class OrdersView(viewsets.GenericViewSet,
                 viewsets.mixins.ListModelMixin,
                 viewsets.mixins.CreateModelMixin):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = ListOrderSerializer
    def get_serializer_class(self):
        if self.action == 'list':
            return ListOrderSerializer
        if self.action == 'create':
            return CreateOrderSerializer
    def get_queryset(self):
        queryset = Order.objects.filter(user=self.request.user)
        return queryset
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if Cart.objects.get(user=request.user).products.all().exists():
            order = serializer.create(request, serializer.validated_data)
            mail_to = order.user.email
            subject = 'Your order'
            text = f'Your order has been created. It will be delivered on {order.date_of_delivery}'
            send_mail(subject=subject, message=text, from_email='my.drf.test@gmail.com', recipient_list=[mail_to])
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Your cart is empty")