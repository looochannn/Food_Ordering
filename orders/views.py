from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings

import razorpay

from .models import Order, OrderItem
from cart.models import Cart


# -------------------------
# CHECKOUT VIEW (CREATE ORDER + REDIRECT TO PAYMENT)
# -------------------------
@login_required
def checkout(request):

    cart = Cart.objects.filter(
        user=request.user,
        is_paid=False
    ).first()

    if not cart:
        return redirect('cart')

    if request.method == "POST":

        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        # 1. CREATE ORDER (NOT PAID YET)
        order = Order.objects.create(
            user=request.user,
            full_name=request.POST.get('full_name'),
            phone=request.POST.get('phone'),
            address=request.POST.get('address'),

            customer_latitude=float(latitude) if latitude else None,
            customer_longitude=float(longitude) if longitude else None,

            total_amount=cart.total_price + 45  # delivery charge
        )

        # 2. CREATE ORDER ITEMS (snapshot)
        for item in cart.cart_items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price  # unit price (correct approach)
            )

        # 3. CREATE RAZORPAY ORDER
        client = razorpay.Client(auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        ))

        payment = client.order.create({
            "amount": int(order.total_amount * 100),  # paise
            "currency": "INR",
            "payment_capture": 1
        })

        # 4. SAVE RAZORPAY ORDER ID
        order.razorpay_order_id = payment['id']
        order.save()

        # 5. SEND TO PAYMENT PAGE
        return render(request, "orders/payment.html", {
            "order": order,
            "payment": payment,
            "razorpay_key": settings.RAZORPAY_KEY_ID
        })

    return render(request, "orders/checkout.html", {
        "cart": cart
    })


# -------------------------
# PAYMENT SUCCESS (CALLED AFTER RAZORPAY)
# -------------------------
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def payment_success(request):

    if request.method == "POST":

        data = json.loads(request.body)

        order = Order.objects.get(uid=data["order_id"])

        order.razorpay_payment_id = data["payment_id"]
        order.razorpay_order_id = data["razorpay_order_id"]
        order.razorpay_signature = data["razorpay_signature"]

        order.payment_status = "PAID"
        order.status = "CONFIRMED"
        order.save()

        # NOW SAFE TO CLEAR CART
        if cart := Cart.objects.filter(user=order.user, is_paid=False).first():
            cart.cart_items.all().delete()
            cart.is_paid = True
            cart.save()

        return JsonResponse({"status": "success"})


# -------------------------
# MY ORDERS VIEW
# -------------------------
@login_required
def my_orders(request):

    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'orders/my_orders.html',
        {
            'orders': orders
        }
    )
# -------------------------
# PAY PENDING ORDER
# -------------------------
@login_required
def pay_pending_order(request, order_id):

    order = Order.objects.filter(
        uid=order_id,
        user=request.user
    ).first()

    if not order:
        return redirect("my_orders")

    # Already paid
    if order.payment_status == "PAID":
        return redirect("my_orders")

    client = razorpay.Client(auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET
    ))

    # Create new Razorpay order
    payment = client.order.create({
        "amount": int(order.total_amount * 100),
        "currency": "INR",
        "payment_capture": 1
    })

    # Save latest Razorpay order id
    order.razorpay_order_id = payment["id"]
    order.save()

    return render(
        request,
        "orders/payment.html",
        {
            "order": order,
            "payment": payment,
            "razorpay_key": settings.RAZORPAY_KEY_ID
        }
    )