from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import Cart, CartItem
from products.models import Product


# -------------------------
# ADD TO CART
# -------------------------
@login_required
def add_to_cart(request, product_uid):

    product = get_object_or_404(
        Product,
        uid=product_uid
    )

    cart, created = Cart.objects.get_or_create(
        user=request.user,
        is_paid=False
    )

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart')


# -------------------------
# CART PAGE
# -------------------------
@login_required
def cart_view(request):

    cart = Cart.objects.prefetch_related(
        'cart_items__product'
    ).filter(
        user=request.user,
        is_paid=False
    ).first()

    cart_count = 0

    if cart:
        cart_count = sum(
            item.quantity
            for item in cart.cart_items.all()
        )

    context = {
        'cart': cart,
        'cart_count': cart_count
    }

    return render(
        request,
        'cart/cart.html',
        context
    )


# -------------------------
# UPDATE QUANTITY
# -------------------------
@login_required
def update_cart(request, item_id):

    item = get_object_or_404(
        CartItem,
        uid=item_id,
        cart__user=request.user
    )

    action = request.GET.get("action")

    if action == "inc":
        item.quantity += 1
        item.save()

    elif action == "dec":

        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()

    return redirect('cart')


# -------------------------
# REMOVE ITEM
# -------------------------
@login_required
def remove_item(request, item_id):

    item = get_object_or_404(
        CartItem,
        uid=item_id,
        cart__user=request.user
    )

    item.delete()

    return redirect('cart')


# -------------------------
# AJAX ADD TO CART
# -------------------------
@login_required
def ajax_add_to_cart(request, product_uid):

    product = get_object_or_404(
        Product,
        uid=product_uid
    )

    cart, created = Cart.objects.get_or_create(
        user=request.user,
        is_paid=False
    )

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    cart_count = sum(
        item.quantity
        for item in cart.cart_items.all()
    )

    return JsonResponse({
        'success': True,
        'cart_count': cart_count
    })