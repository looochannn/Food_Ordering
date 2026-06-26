from django.shortcuts import render
from products.models import Restaurant, Category


def home(request):

    restaurants = Restaurant.objects.all()
    categories = Category.objects.all()

    # Search Restaurant
    search = request.GET.get('search')

    if search:
        restaurants = restaurants.filter(
            name__icontains=search
        )

    # Category Filter
    category_id = request.GET.get('category')

    if category_id:
        restaurants = restaurants.filter(
            products__category__uid=category_id   # products__category__id is the foreign key of category where id is the primary key of category table
        ).distinct()

    context = {
        'restaurants': restaurants,
        'categories': categories,
    }

    return render(
        request,
        'home/home.html',
        context
    )