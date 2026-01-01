# vendors/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Vendor, Withdrawal
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponseForbidden
from .models import *
from .forms import *
@login_required
def vendor_dashboard(request):
    try:
        vendor = request.user.vendor  # This assumes a OneToOneField with related_name='vendor'
    except Vendor.DoesNotExist:
        return HttpResponseForbidden("You are not authorized to access the vendor dashboard.")
    
    
    # Total products added by the vendor
    total_products = Product.objects.filter(vendor=vendor).count()

    # Orders containing the vendor's products
    order_items = OrderItem.objects.filter(product__vendor=vendor)
    total_orders = order_items.values('order').distinct().count()

    # Orders by status
    orders_by_status = order_items.values('order__status').annotate(count=Count('order__id'))

    # Prepare status counts
    status_counts = {
        'Pending': 0,
        'Processing': 0,
        'Shipped': 0,
        'Delivered': 0,
        'Cancelled': 0,
    }
    for item in orders_by_status:
        status = item['order__status']
        count = item['count']
        status_counts[status] = count

    context = {
        'vendor': vendor,
        'total_products': total_products,
        'total_orders': total_orders,
        'pending_orders': status_counts['Pending'],
        'processing_orders': status_counts['Processing'],
        'shipped_orders': status_counts['Shipped'],
        'delivered_orders': status_counts['Delivered'],
        'cancelled_orders': status_counts['Cancelled'],
    }

    return render(request, 'vendor/vendor_dashboard.html', context)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Vendor, ProductColorVariant, ProductSizeVariant
from .forms import *

@login_required
def product_dashboard(request):
    vendor = get_object_or_404(Vendor, user=request.user)
    products = Product.objects.filter(vendor=vendor)
    return render(request, 'vendor/manage-products.html', {'products': products})

@login_required
def add_product(request):
    vendor = get_object_or_404(Vendor, user=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = vendor
            product.created_by = request.user
            product.save()
            return redirect('product_dashboard')
    else:
        form = ProductForm()
    return render(request, 'vendor/add_edit_product.html', {'form': form, 'title': 'Add Product'})

@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk, vendor__user=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_dashboard')
    else:
        form = ProductForm(instance=product)
    return render(request, 'vendor/add_edit_product.html', {'form': form, 'title': 'Edit Product'})

@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk, vendor__user=request.user)
    product.delete()
    return redirect('product_dashboard')

@login_required
def manage_variants(request, product_id):
    product = get_object_or_404(Product, id=product_id, vendor__user=request.user)
    color_variants = ProductColorVariant.objects.filter(product=product)
    size_variants = ProductSizeVariant.objects.filter(product=product)
    return render(request, 'vendor/manage_variants.html', {
        'product': product,
        'color_variants': color_variants,
        'size_variants': size_variants
    })

@login_required
def add_color_variant(request, product_id):
    product = get_object_or_404(Product, id=product_id, vendor__user=request.user)
    if request.method == 'POST':
        form = ProductColorVariantForm(request.POST, request.FILES)
        if form.is_valid():
            variant = form.save(commit=False)
            variant.product = product
            variant.save()
            return redirect('manage_variants', product_id=product.id)
    else:
        form = ProductColorVariantForm()
    return render(request, 'vendor/add_edit_variant.html', {
        'form': form,
        'title': 'Add Color Variant',
        'product': product  # Important for template reverse lookup
    })

@login_required
def add_size_variant(request, product_id):
    product = get_object_or_404(Product, id=product_id, vendor__user=request.user)
    if request.method == 'POST':
        form = ProductSizeVariantForm(request.POST, request.FILES)
        if form.is_valid():
            variant = form.save(commit=False)
            variant.product = product
            variant.save()
            return redirect('manage_variants', product_id=product.id)
    else:
        form = ProductSizeVariantForm()
    return render(request, 'vendor/add_edit_variant.html', {
        'form': form,
        'title': 'Add Size Variant',
        'product': product  # Important for template reverse lookup
    })
@login_required
def edit_color_variant(request, product_id, variant_id):
    product = get_object_or_404(Product, id=product_id, vendor__user=request.user)
    variant = get_object_or_404(ProductColorVariant, id=variant_id, product=product)

    if request.method == 'POST':
        form = ProductColorVariantForm(request.POST, request.FILES, instance=variant)
        if form.is_valid():
            form.save()
            return redirect('manage_variants', product_id=product.id)
    else:
        form = ProductColorVariantForm(instance=variant)

    return render(request, 'vendor/add_edit_variant.html', {
        'form': form,
        'title': 'Edit Color Variant',
        'product': product
    })
@login_required
def delete_color_variant(request, product_id, variant_id):
    product = get_object_or_404(Product, id=product_id, vendor__user=request.user)
    variant = get_object_or_404(ProductColorVariant, id=variant_id, product=product)
    variant.delete()
    return redirect('manage_variants', product_id=product.id)
@login_required
def edit_size_variant(request, product_id, variant_id):
    product = get_object_or_404(Product, id=product_id, vendor__user=request.user)
    variant = get_object_or_404(ProductSizeVariant, id=variant_id, product=product)

    if request.method == 'POST':
        form = ProductSizeVariantForm(request.POST, request.FILES, instance=variant)
        if form.is_valid():
            form.save()
            return redirect('manage_variants', product_id=product.id)
    else:
        form = ProductSizeVariantForm(instance=variant)

    return render(request, 'vendor/add_edit_variant.html', {
        'form': form,
        'title': 'Edit Size Variant',
        'product': product
    })
@login_required
def delete_size_variant(request, product_id, variant_id):
    product = get_object_or_404(Product, id=product_id, vendor__user=request.user)
    variant = get_object_or_404(ProductSizeVariant, id=variant_id, product=product)
    variant.delete()
    return redirect('manage_variants', product_id=product.id)
@login_required
def manage_orders(request):
    vendor_products = Product.objects.filter(vendor=request.user.vendor)

    # Get OrderItems related to this vendor's products
    sold_items = OrderItem.objects.filter(product__in=vendor_products).select_related('order')

    # Extract orders from those items
    vendor_orders = Order.objects.filter(id__in=sold_items.values_list('order_id', flat=True).distinct())

    # Orders where this vendor purchased from others
    my_orders = Order.objects.filter(user=request.user)

    return render(request, 'vendor/manage_orders.html', {
        'vendor_orders': vendor_orders,
        'my_orders': my_orders,
    })
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.contrib import messages  # Optional: if you want to show messages
from .models import Order, OrderItem, Vendor, Product  # Update based on your actual models


@login_required
def vendor_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    vendor = get_object_or_404(Vendor, user=request.user)

    # Only show items for this vendor
    order_items = OrderItem.objects.filter(order=order, product__vendor=vendor)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'mark_processing' and order.status == 'Pending':
            # Check stock before updating
            stock_issue = False
            for item in order_items:
                if item.product.stock < item.quantity:
                    stock_issue = True
                    messages.error(request, f"Insufficient stock for product '{item.product.name}'.")
                    break

            if not stock_issue:
                for item in order_items:
                    product = item.product
                    product.stock -= item.quantity
                    product.save()

                order.status = 'Processing'
                order.save()
                messages.success(request, "Order marked as Processing and stock updated.")

        elif action == 'mark_shipped' and order.status == 'Processing':
            order.status = 'Shipped'
            order.shipped_at = timezone.now()
            order.save()
            messages.success(request, "Order marked as Shipped.")

        elif action == 'mark_delivered' and order.status == 'Shipped':
            order.status = 'Delivered'
            order.delivered_at = timezone.now()
            order.save()
            messages.success(request, "Order marked as Delivered.")

        elif action == 'update_shipping':
            order.courier = request.POST.get('courier')
            order.tracking_number = request.POST.get('tracking_number')
            order.estimated_delivery = request.POST.get('estimated_delivery')
            order.save()
            messages.success(request, "Shipping information updated.")

        return redirect('vendor_order_detail', order_id=order_id)

    return render(request, 'vendor/order_detail.html', {
        'order': order,
        'order_items': order_items,
    })

@login_required
def payment_history(request):
    payments = Payment.objects.filter(order__user=request.user).select_related('order').order_by('-order__created_at')
    latest_payment = payments.first()
    return render(request, 'vendor/payment_history.html', {
        'payments': payments,
        'latest_payment': latest_payment
    })
from django.core.paginator import Paginator
from django.db.models import Q
@login_required
def order_history(request):
    query = request.GET.get('q', '').strip()
    orders = Order.objects.filter(user=request.user)

    if query:
        orders = orders.filter(
            Q(id__icontains=query) | Q(status__icontains=query)
        )

    paginator = Paginator(orders.order_by('-created_at'), 10)  # 10 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'vendor/order_history.html', {
        'orders': page_obj,
        'query': query
    })
@login_required
def vendor_payment_details(request):
    vendor = get_object_or_404(Vendor, user=request.user)

    if request.method == 'POST':
        form = VendorBankForm(request.POST, instance=vendor)
        if form.is_valid():
            form.save()
            return redirect('vendor_payment_details')
    else:
        form = VendorBankForm(instance=vendor)

    return render(request, 'vendor/payment_details.html', {
        'form': form,
        'vendor': vendor,
    })
@login_required
def edit_vendor_profile(request):
    vendor = get_object_or_404(Vendor, user=request.user)

    if request.method == 'POST':
        form = VendorProfileForm(request.POST, request.FILES, instance=vendor)
        if form.is_valid():
            form.save()
            return redirect('edit_profile') 
    else:
        form = VendorProfileForm(instance=vendor)

    return render(request, 'vendor/edit_profile.html', {'form': form})
@login_required
def update_product_stock(request, product_id):
    vendor = get_object_or_404(Vendor, user=request.user)
    product = get_object_or_404(Product, id=product_id, vendor=vendor)

    if request.method == 'POST':
        form = ProductStockForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Stock Updated successfully.")
            return redirect('product_dashboard')  
    else:
        form = ProductStockForm(instance=product)

    return render(request, 'vendor/update_stock.html', {'form': form, 'product': product})
from decimal import Decimal
@login_required
def vendor_earnings(request):
    vendor = Vendor.objects.get(user=request.user)

    # 1. Calculate total earnings from delivered orders
    delivered_items = OrderItem.objects.filter(
        product__vendor=vendor,
        order__status='Delivered'
    )
    total_earned = sum(item.price * item.quantity for item in delivered_items)
    vendor.total_earnings = total_earned

    # 2. Subtract withdrawals (pending or approved)
    total_withdrawn = Withdrawal.objects.filter(
        vendor=vendor,
        status__in=['Pending', 'Approved']
    ).aggregate(total=models.Sum('amount'))['total'] or 0

    vendor.available_balance = total_earned - total_withdrawn
    vendor.save()

    # 3. Get withdrawal history
    withdrawals = Withdrawal.objects.filter(vendor=vendor).order_by('-requested_at')

    # 4. Handle withdrawal form
    if request.method == 'POST':
        amount = request.POST.get('amount')

        if not amount:
            messages.error(request, "Withdrawal amount is required.")
            return redirect('vendor_earnings')

        try:
            amount = float(amount)
        except ValueError:
            messages.error(request, "Invalid withdrawal amount.")
            return redirect('vendor_earnings')

        if not all([vendor.bank_name, vendor.account_holder_name, vendor.account_number, vendor.swift_code]):
            messages.error(request, "Withdrawal failed! Bank details are missing.")
            return redirect('vendor_earnings')

        if amount <= vendor.available_balance and amount > 0:
            Withdrawal.objects.create(vendor=vendor, amount=amount)

            # Send email to admin and vendor
            send_mail(
                subject=f"[eMarket] Withdrawal Request from {vendor.business_name}",
                message=(
                    f"Vendor '{vendor.business_name}' (Username: {vendor.user.username}) has requested a withdrawal of PKR {amount:.2f}.\n\n"
                    f"Requested at: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"Bank: {vendor.bank_name}\n"
                    f"Account #: {vendor.account_number}\n\n"
                    "This request is pending approval from admin."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL, vendor.user.email],
            )

            messages.success(request, "Withdrawal request submitted!")
        else:
            messages.error(request, "Invalid withdrawal amount or insufficient balance.")

        return redirect('vendor_earnings')

    return render(request, 'vendor/vendor_earnings.html', {
        'vendor': vendor,
        'withdrawals': withdrawals,
    })