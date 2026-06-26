from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def login_page(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            username=username,
            password=password
        )

        if user:
            login(request, user)
            return redirect("/")

        messages.error(
            request,
            "Invalid username or password"
        )

    return render(
        request,
        "authentication/login.html"
    )


def register_page(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(
            username=username
        ).exists():

            messages.error(
                request,
                "Username already exists"
            )

            return redirect("register")

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(
            request,
            "Account created successfully"
        )

        return redirect("login")

    return render(
        request,
        "authentication/register.html"
    )


def logout_page(request):

    logout(request)

    return redirect("/")
@login_required
def settings_page(request):
    return render(
        request,
        "authentication/settings.html"
    )