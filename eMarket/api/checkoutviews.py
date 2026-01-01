from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from .models import *
import datetime
import re

User = get_user_model()

def checkout_view(request):
    cart = Cart.get_or_create_cart(request)

    if not cart.items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('cart_view')

    if request.method == "POST":
        # Get data from form
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()
        zip_code = request.POST.get('zip_code', '').strip()
        card_number = request.POST.get('card_number', '').strip()
        expiry = request.POST.get('expiry', '').strip()
        cvv = request.POST.get('cvv', '').strip()
        password = request.POST.get('password', '').strip() if not request.user.is_authenticated else None

        form_data = {
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "address": address,
            "city": city,
            "zip_code": zip_code,
            "card_number": card_number,
            "expiry": expiry,
            "cvv": cvv,
            "password": password,
        }

        errors = {}

        # Basic validations
        if not full_name:
            errors["full_name"] = "Full name is required."
        if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            errors["email"] = "A valid email is required."
        if not phone or not re.match(r"^[0-9+\-\s]{10,15}$", phone):
            errors["phone"] = "A valid phone number is required."
        if not address:
            errors["address"] = "Address is required."
        if not city:
            errors["city"] = "City is required."
        if not zip_code or not zip_code.isdigit():
            errors["zip_code"] = "A valid zip code is required."

        # Card validations
        if not card_number.isdigit() or len(card_number) != 16:
            errors["card_number"] = "Card number must be 16 digits."
        elif not card_number.startswith(('4', '5')):
            errors["card_number"] = "Only Visa (starts with 4) and MasterCard (starts with 5) are accepted."

        # Expiry date
        if not expiry or not re.match(r"^(0[1-9]|1[0-2])\/\d{2}$", expiry):
            errors["expiry"] = "Expiry must be in MM/YY format."
        else:
            try:
                exp_month, exp_year = map(int, expiry.split("/"))
                exp_year += 2000
                now = datetime.datetime.now()
                exp_date = datetime.datetime(exp_year, exp_month, 1)
                if exp_date < now.replace(day=1):
                    errors["expiry"] = "Card has expired."
            except ValueError:
                errors["expiry"] = "Invalid expiry date."

        # CVV
        if not cvv or not cvv.isdigit() or len(cvv) not in [3, 4]:
            errors["cvv"] = "CVV must be 3 or 4 digits."

        # Password validation if user not logged in
        if not request.user.is_authenticated:
            if not password or len(password) < 6:
                errors["password"] = "Password must be at least 6 characters long."

        if errors:
            for field, error in errors.items():
                messages.error(request, f"{field.capitalize()}: {error}")
            return render(request, "purchase/checkout.html", {
                "form_data": form_data,
                "errors": errors,
                "cart": cart
            })

        # Create user if not authenticated
        if not request.user.is_authenticated:
            user, created = User.objects.get_or_create(email=email)
            if created:
                username = email.split('@')[0] + get_random_string(4)
                user.username = username
                user.set_password(password)
                user.save()
            # If user exists but has no usable password, update it
            elif not user.has_usable_password():
                user.set_password(password)
                user.save()
        else:
            user = request.user

        # Create order
        order = Order.objects.create(
            user=user,
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            zip_code=zip_code,
            total_amount=cart.total_amount(),
            status="Pending"
        )

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                color=item.color.color_name if item.color else '',
                size=item.size.size_label if item.size else '',
                price=item.total_price / item.quantity,
                quantity=item.quantity
            )

        # Save payment (masked)
        Payment.objects.create(
            order=order,
            card_number=card_number[-4:].rjust(16, "*"),
            expiry=expiry,
            cvv="***",
            payment_status="Success"
        )

        # Send email
        subject = f"Order Confirmation - #{order.id}"
        html_content = render_to_string("purchase/order_confirmation.html", {
            "order": order,
            "items": order.items.all(),
            "new_user": not request.user.is_authenticated
        })
        email_message = EmailMultiAlternatives(subject, '', to=[email])
        email_message.attach_alternative(html_content, "text/html")
        email_message.send()

        # Clear cart
        cart.items.all().delete()

        messages.success(request, f"Order #{order.id} placed successfully!")
        return redirect("order_confirmation", order_id=order.id)

    return render(request, "purchase/checkout.html", {"cart": cart})

def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'purchase/order_success.html', {'order': order})
