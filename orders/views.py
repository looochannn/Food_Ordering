from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

import razorpay
import json

from .models import Order, OrderItem
from cart.models import Cart


# =====================================================
# CHECKOUT
# =====================================================

@login_required
def checkout(request):

    cart = Cart.objects.filter(
        user=request.user,
        is_paid=False
    ).first()

    if not cart:
        return redirect("cart")

    if request.method == "POST":

        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")

        # Create Order
        order = Order.objects.create(
            user=request.user,
            full_name=request.POST.get("full_name"),
            phone=request.POST.get("phone"),
            address=request.POST.get("address"),

            customer_latitude=float(latitude) if latitude else None,
            customer_longitude=float(longitude) if longitude else None,

            total_amount=cart.total_price + 45
        )

        # Save Ordered Items
        for item in cart.cart_items.all():

            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        # Razorpay Client
        client = razorpay.Client(auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        ))

        payment = client.order.create({

            "amount": int(order.total_amount * 100),

            "currency": "INR",

            "payment_capture": 1

        })

        # Save Razorpay Order Id
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

    return render(

        request,

        "orders/checkout.html",

        {

            "cart": cart

        }

    )
# =====================================================
# PAYMENT SUCCESS
# =====================================================

@login_required
@csrf_exempt
def payment_success(request):

    if request.method != "POST":
        return JsonResponse(
            {
                "status": "Invalid Request"
            },
            status=400
        )

    try:

        data = json.loads(request.body)

        order = Order.objects.filter(uid=data["order_id"],user=request.user).first()

        if not order:
            return JsonResponse({"status": "Invalid Order"}, status=404)
        # Already paid
        if order.payment_status == "PAID":
            return JsonResponse({
        "status": "already_paid"
            })

        client = razorpay.Client(auth=(

            settings.RAZORPAY_KEY_ID,

            settings.RAZORPAY_KEY_SECRET

        ))

        # -------------------------------------
        # VERIFY PAYMENT SIGNATURE
        # -------------------------------------

        params_dict = {

            "razorpay_order_id": data["razorpay_order_id"],

            "razorpay_payment_id": data["payment_id"],

            "razorpay_signature": data["razorpay_signature"]

        }

        client.utility.verify_payment_signature(
            params_dict
        )

        # -------------------------------------
        # SAVE PAYMENT DETAILS
        # -------------------------------------

        order.razorpay_payment_id = data["payment_id"]

        order.razorpay_order_id = data["razorpay_order_id"]

        order.razorpay_signature = data["razorpay_signature"]

        order.payment_status = "PAID"

        order.status = "CONFIRMED"

        order.save()

        # -------------------------------------
        # CLEAR USER CART
        # -------------------------------------

        if cart := Cart.objects.filter(

            user=order.user,

            is_paid=False

        ).first():

            cart.cart_items.all().delete()

            cart.is_paid = True

            cart.save()

        # -------------------------------------
        # SEND EMAIL
        # -------------------------------------

        if order.user.email:

            subject = f"🍔 FoodHub - Order Confirmed ({order.uid})"

            text_content = render_to_string(
                "emails/order_confirmation.txt",
                {"order": order}
            )

            html_content = render_to_string(
                "emails/order_confirmation.html",
                {"order": order}
            )

            email = EmailMultiAlternatives(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [order.user.email]
            )

            email.attach_alternative(
                html_content,
                "text/html"
            )

            try:
                email.send()

            except Exception as e:
                print("Email Error:", e)

        return JsonResponse({

            "status": "success"

        })

    except razorpay.errors.SignatureVerificationError:

        return JsonResponse({

            "status": "Payment Verification Failed"

        }, status=400)

    except Exception as e:

        return JsonResponse({

            "status": str(e)

        }, status=500)
    # =====================================================
# MY ORDERS
# =====================================================

@login_required
def my_orders(request):

    orders = Order.objects.filter(
        user=request.user
    ).prefetch_related(
        "items",
        "items__product"
    ).order_by("-created_at")

    return render(
        request,
        "orders/my_orders.html",
        {
            "orders": orders
        }
    )


# =====================================================
# PAY PENDING ORDER
# =====================================================

@login_required
def pay_pending_order(request, order_id):

    order = Order.objects.filter(
        uid=order_id,
        user=request.user
    ).first()

    if not order:
        return redirect("my_orders")

    # Already Paid
    if order.payment_status == "PAID":
        return redirect("my_orders")

    client = razorpay.Client(auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET
    ))

    payment = client.order.create({

        "amount": int(order.total_amount * 100),

        "currency": "INR",

        "payment_capture": 1

    })

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
# =====================================================
# PAYMENT FAILED
# =====================================================

@login_required
def payment_failed(request):

    return render(
        request,
        "orders/payment_failed.html"
    )