from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Product, Category

from django.shortcuts import render
from .models import Product, Category

def shop_view(request):
    products = Product.objects.filter(is_available=True)
    categories = Category.objects.all()
    selected_category = request.GET.get('category')
    search_query = request.GET.get('q')
    sort_by = request.GET.get('sort')

    # Filter by category
    if selected_category:
        products = products.filter(category_id=selected_category)

    # Search
    if search_query:
        products = products.filter(name__icontains=search_query)

    # Sorting
    if sort_by == 'price_low':
        products = products.order_by('base_price')
    elif sort_by == 'price_high':
        products = products.order_by('-base_price')

    context = {
        'products': products,
        'categories': categories,
        'selected_category': int(selected_category) if selected_category else None,
    }
    return render(request, 'shop.html', context)
