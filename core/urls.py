from django.urls import path
from .views import (
    CheckoutView,
    add_to_cart,
    contactView,
    successView,
    HomeView,
    OrderSummaryView,
    ItemDetailView,
    remove_from_cart,
    remove_single_item_from_cart,
    add_single_item_to_cart,
    PaymentView,
    # add_coupon
)

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('checkout-page/', CheckoutView.as_view(), name='checkout-page'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('contact/', contactView, name='contact'),
    path('success/', successView, name='success'),
    # path('add-coupon/<code>/', add_coupon, name='add-coupon'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart, name='remove-single-item-from-cart'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment')
]