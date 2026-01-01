from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Cart, CartItem, Product, ProductColorVariant, ProductSizeVariant, Coupon
from decimal import Decimal
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Coupon, Cart

def cart_view(request):
    cart = Cart.get_or_create_cart(request)
    cart.update_totals()
    items = cart.items.select_related('product', 'color', 'size')

    subtotal = sum(item.total_price for item in items)

    context = {
        'cart': cart,
        'items': items,
        'subtotal': f"{subtotal:,.2f}",  
        'total': f"{cart.total:,.2f}",
    }
    return render(request, 'purchase/cart.html', context)


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    color_id = request.POST.get('color')
    size_id = request.POST.get('size')
    quantity = int(request.POST.get('quantity', 1))

    color = ProductColorVariant.objects.filter(id=color_id).first() if color_id else None
    size = ProductSizeVariant.objects.filter(id=size_id).first() if size_id else None

    cart = Cart.get_or_create_cart(request)
    item, created = CartItem.objects.get_or_create(
        cart=cart, product=product, color=color, size=size,
        defaults={'quantity': quantity}
    )
    if not created:
        item.quantity += quantity
        item.save()

    cart.update_totals()
    return redirect('cart_view')


def update_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        item.quantity = quantity
        item.save()
        item.cart.update_totals()
        messages.success(request, 'Cart updated successfully.')
    return redirect('cart_view')

def remove_cart_item(request, item_id):
    try:
        cart_item = CartItem.objects.get(id=item_id
                                         )
        cart_item.delete()
        messages.success(request, "Item removed successfully.")
    except CartItem.DoesNotExist:
        messages.warning(request, "That cart item no longer exists.")
    return redirect('cart_view')

def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('coupon_code', '').strip()
        cart = Cart.get_or_create_cart(request)

        try:
            coupon = Coupon.objects.get(code__iexact=code, active=True)
            if not coupon.can_be_used() or coupon.is_expired():
                messages.error(request, "This coupon is expired or invalid.")
                return redirect('cart')

            if coupon.valid_from and timezone.now() < coupon.valid_from:
                messages.error(request, "This coupon is not valid yet.")
                return redirect('cart')
            if coupon.valid_to and timezone.now() > coupon.valid_to:
                messages.error(request, "This coupon has expired.")
                return redirect('cart')
            if not coupon.is_valid_for_user(request.user):
                messages.error(request, "This coupon is not valid for your account.")
                return redirect('cart')

            cart.coupon = coupon
            cart.update_totals()
            coupon.uses_count += 1
            coupon.save()
            messages.success(request, f"Coupon '{coupon.code}' applied successfully!")
        except Coupon.DoesNotExist:
            messages.error(request, "Invalid coupon code.")
    return redirect('cart_view')
def remove_coupon(request):
    cart = Cart.objects.get(user=request.user)
    if cart.coupon:
        cart.coupon = None
        cart.save()
        cart.update_totals()
        messages.success(request, "Coupon removed successfully.")
    else:
        messages.info(request, "No coupon was applied.")
    return redirect('cart_view')  # Or use the name of your cart page