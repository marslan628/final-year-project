from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from .models import *
from .forms import ReviewForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template.loader import render_to_string
class ProductListView(ListView):
    model = Product
    template_name = 'products/products_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        """
        Return filtered queryset if a category slug is present in the URL.
        Otherwise, return all available products.
        """
        category_slug = self.kwargs.get('slug')
        queryset = Product.objects.filter(is_available=True)

        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=category)

        return queryset

    def get_context_data(self, **kwargs):
        """
        Adds categories, brands, and colors to the context for the sidebar filters.
        """
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()

        # Unique brand list from available products
        context['brands'] = Product.objects.filter(is_available=True) \
                                           .values_list('brand', flat=True) \
                                           .distinct()

        # Get all available colors (avoid querying through product relation)
        context['colors'] = ProductColorVariant.objects.all()

        return context
from django.db.models import Avg
class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()

        # Variant price map
        variant_map = {}
        for size in product.size_variants.all():
            for color in product.color_variants.all():
                price = product.base_price + size.price + color.price
                key = f"{size.id}_{color.id}"
                variant_map[key] = float(price)

        # Reviews
        reviews = product.reviews.select_related('user').order_by('-created_at')
        avg_rating = product.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        user_review = None
        if self.request.user.is_authenticated:
            user_review = product.reviews.filter(user=self.request.user).first()

        context.update({
            'variant_price_map': json.dumps(variant_map),
            'review_form': ReviewForm(instance=user_review),
            'reviews': reviews,
            'avg_rating': round(avg_rating, 1),
            'user_review': user_review,
            'related_products': Product.objects.filter(category=product.category).exclude(id=product.id)[:3],
        })
        return context
from django.views.decorators.http import require_GET, require_POST
@require_POST
@login_required
def add_review(request, slug):
    product = get_object_or_404(Product, slug=slug)
    existing_review = Review.objects.filter(product=product, user=request.user).first()

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            if existing_review:
                messages.success(request, "Your review was updated.")
            else:
                messages.success(request, "Thank you for your review!")
        else:
            messages.error(request, "There was an error with your review.")

    return redirect('product_detail', slug=slug)

def search_products(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')

    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query)

    if category_id:
        products = products.filter(category_id=category_id)

    categories = Category.objects.all()
    return render(request, 'products/products_list.html', {
        'products': products,
        'categories': categories,
        'query': query
    })

def ajax_filter_products(request):
    category_ids = request.GET.getlist('categories[]')
    products = Product.objects.all()

    if category_ids:
        products = products.filter(category__id__in=category_ids)

    html = render_to_string('products/product_list_ajax.html', {'products': products})
    return JsonResponse({'html': html})
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def add_to_cart(request):
    if request.method == "POST" and request.user.is_authenticated:
        data = json.loads(request.body)
        product_id = data.get("product_id")
        quantity = int(data.get("quantity", 1))
        # Add to cart logic here (e.g., Cart.objects.create(...))
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "message": "Unauthorized or invalid request"})
def quick_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'partials/quick_view_modal.html', {'product': product})