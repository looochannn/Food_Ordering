from django.urls import path
from .views import restaurant_detail

urlpatterns = [
    path(
        'restaurant/<uuid:uid>/',
        restaurant_detail,
        name='restaurant_detail'
    ),
]