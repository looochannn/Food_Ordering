from django.urls import path
from . import views

urlpatterns = [

    # Checkout
    path(
        'checkout/',
        views.checkout,
        name='checkout'
    ),

    # Retry payment for pending order
    path(
        'pay/<uuid:order_id>/',
        views.pay_pending_order,
        name='pay_pending_order'
    ),

    # Razorpay payment success
    path(
        'payment-success/',
        views.payment_success,
        name='payment_success'
    ),

    # My Orders
    path(
        'my-orders/',
        views.my_orders,
        name='my_orders'
    ),

]