from django.shortcuts import render, get_object_or_404

from .models import Restaurant


def restaurant_detail(request, uid):

    restaurant = get_object_or_404(
        Restaurant,
        uid=uid
    )

    products = restaurant.products.all()

    # Menu Search
    search = request.GET.get('search')

    if search:
        products = products.filter(
            product_name__icontains=search
        )

    context = {
        'restaurant': restaurant,
        'products': products,
    }

    return render(
        request,
        'products/restaurant_detail.html',
        context
    )