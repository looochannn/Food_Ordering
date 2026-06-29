from django.urls import path
from . import views

urlpatterns = [

    path(
        "checkout/",
        views.checkout,
        name="checkout"
    ),

    path(
        "payment-success/",
        views.payment_success,
        name="payment_success"
    ),

    path(
        "my-orders/",
        views.my_orders,
        name="my_orders"
    ),

    path(
        "pay/<uuid:order_id>/",
        views.pay_pending_order,
        name="pay_pending_order"
    ),

]