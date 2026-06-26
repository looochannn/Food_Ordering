from django.urls import path
from .views import (
    add_to_cart,
    cart_view,
    update_cart,
    remove_item,
    ajax_add_to_cart
)

urlpatterns = [
    path('add/<uuid:product_uid>/', add_to_cart, name='add_to_cart'),
    path('', cart_view,name='cart'),
    path('update/<uuid:item_id>/', update_cart, name='update_cart'),
    path('remove/<uuid:item_id>/',remove_item,name='remove_item'),
    path('ajax/add/<uuid:product_uid>/', ajax_add_to_cart, name='ajax_add_to_cart'),
]