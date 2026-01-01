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

def add_to_cart(request):
    if request.method == "POST":
        product_id = request.POST.get('product_id')
        try:
            quantity = max(int(request.POST.get('quantity', 1)), 1)
        except (TypeError, ValueError):
            quantity = 1

        color_id = request.POST.get('color_id')
        size_id = request.POST.get('size_id')

        product = get_object_or_404(Product, id=product_id)
        color = ProductColorVariant.objects.filter(id=color_id).first() if color_id else None
        size = ProductSizeVariant.objects.filter(id=size_id).first() if size_id else None

        cart = Cart.get_or_create_cart(request)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            color=color,
            size=size,
        )

        if created:
            cart_item.quantity = quantity
        else:
            cart_item.quantity += quantity
        cart_item.save()

        messages.success(request, f"{product.name} added to cart.")
        return redirect('cart_view')

    return JsonResponse({'error': 'Invalid request'}, status=400)
