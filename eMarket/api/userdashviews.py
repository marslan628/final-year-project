from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import *

@login_required
def customer_dashboard(request):
    # Get all orders belonging to the logged-in user
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    # Aggregate order counts by status
    context = {
        'orders': orders,
        'total_orders': orders.count(),
        'pending_orders': orders.filter(status='Pending').count(),
        'delivered_orders': orders.filter(status='Delivered').count(),
        'cancelled_orders': orders.filter(status='Cancelled').count(),
        'shipped_orders': orders.filter(status='Shipped').count(),
    }

    return render(request, 'customers/customer_dashboard.html', context)
from django.shortcuts import render, get_object_or_404
from .models import Order

def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'customers/order_detail.html', {'order': order})
login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'customers/my_orders.html', {'orders': orders})
from django.shortcuts import get_object_or_404
from .models import ProductColorVariant, ProductSizeVariant
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages 
@login_required
def reorder_view(request, order_id):
    # Fetch the original order for the logged-in user
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Create or get the user's cart
    cart, created = Cart.objects.get_or_create(user=request.user, session_key=None)

    for order_item in order.items.all():
        # Get color variant if color exists and is a string
        color = None
        if order_item.color:
            color = ProductColorVariant.objects.filter(
                product=order_item.product, color_name=order_item.color
            ).first()

        # Get size variant if size exists and is a string
        size = None
        if order_item.size:
            size = ProductSizeVariant.objects.filter(
                product=order_item.product, size_label=order_item.size
            ).first()

        # Add the product to the cart
        CartItem.objects.create(
            cart=cart,
            product=order_item.product,
            color=color,
            size=size,
            quantity=order_item.quantity
        )

    messages.success(request, f"Order #{order.id} has been added to your cart.")
    return redirect('cart_view')
def track_order_view(request):
    order = None
    searched = False

    if request.method == 'POST':
        query = request.POST.get('query')
        searched = True

        if query.isdigit():
            order = Order.objects.filter(id=query).first()
        else:
            order = Order.objects.filter(email__iexact=query).last()

    return render(request, 'customers/track_order.html', {'order': order, 'searched': searched})
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

    return render(request, 'customers/order_history.html', {
        'orders': page_obj,
        'query': query
    })
  