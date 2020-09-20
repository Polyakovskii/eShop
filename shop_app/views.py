from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from .models import Product, Cart, Order, ProductInCart
from .serializers import ListProductSerializer,\
        SingleProductSerializer, \
        CreateProductSerializer, \
        CartSerializer, \
        UpdateProductInCartSerializer, \
        ListOrderSerializer, \
        CreateOrderSerializer, \
        CreateProductInCartSerializer, \
        UserSerializer
from .filters import ProductFilter
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import IsAdminOrReadOnly
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from eShop.settings import EMAIL_HOST_USER


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
            cart = Cart.objects.get(user=request.user)
            return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            cart = Cart.objects.create(user=request.user)
            return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CreateProductInCartSerializer(data=request.data)
        if serializer.is_valid():
            try:
                cart = Cart.objects.get(user=request.user)
            except ObjectDoesNotExist:
                cart = Cart.objects.create(user=request.user)
            cart.add_product(serializer.create(serializer.validated_data))
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        serializer = UpdateProductInCartSerializer(data=request.data)
        if serializer.is_valid():
            serializer.instance = ProductInCart.objects.get(pk=serializer.validated_data.get('id'))
            serializer.save()
            return Response(status=status.HTTP_202_ACCEPTED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


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
        if not Cart.objects.get(user=request.user).is_empty():
            order = serializer.create(request, serializer.validated_data)
            mail_to = order.user.email
            subject = 'Your order'
            text = f'Your order has been created. It will be delivered on {order.date_of_delivery}'
            send_mail(subject=subject, message=text, from_email=EMAIL_HOST_USER, recipient_list=[mail_to])
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Your cart is empty")


class UserCreateView(viewsets.GenericViewSet, viewsets.mixins.CreateModelMixin):

    queryset = User.objects.all()
    serializer_class = UserSerializer
