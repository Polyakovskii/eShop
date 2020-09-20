from django.urls import path
from .views import ProductView, CartView, OrdersView, UserCreateView

urlpatterns = [
    path('products', ProductView.as_view({'get': 'list', 'post': 'create'})),
    path('products/<int:pk>', ProductView.as_view({'get' :'retrieve'})),
    path('carts', CartView.as_view()),
    path('orders', OrdersView.as_view({'get':'list', 'post':'create'})),
    path('registration', UserCreateView.as_view({'post':'create'}))
]