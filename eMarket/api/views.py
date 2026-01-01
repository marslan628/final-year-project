from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from django.http import JsonResponse, Http404
import random
from .forms import *
def chunk_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def home(request):
    top_vendors = Vendor.objects.annotate(
        product_count=models.Count('products')
    ).order_by('-product_count')[:4]
    featured_category = get_object_or_404(Category, slug='electronics') 
    electronics_category = Category.objects.get(slug="electronics")  
    electronics_products = Product.objects.filter(category=electronics_category, is_available=True)[:3]
    deals_category = Category.objects.get(slug="deals")  
    deals_products = Product.objects.filter(category=deals_category, is_available=True)[:3]
    mens_category = Category.objects.get(slug="mens-fashion")  
    mens_products = Product.objects.filter(category=mens_category, is_available=True)[:3]
    women_category = Category.objects.get(slug="women-fashion")  
    women_products = Product.objects.filter(category=women_category, is_available=True)[:3]
    products = Product.objects.filter(category=featured_category, is_available=True)
    
    selected_category_id = request.GET.get('category')
    categories = Category.objects.all()
    for vendor in top_vendors:
        vendor.rating_float = float(vendor.average_rating)
    badge_options = {
        'New': 'bg-primary',
        'Popular': 'bg-success',
        'Hot': 'bg-danger',
        'Trending': 'bg-warning text-dark',
        'Top': 'bg-dark'
    }

    for category in categories:
        badge = random.choice(list(badge_options.keys()))
        category.badge = badge
        category.badge_color = badge_options[badge]

    if selected_category_id:
        try:
            selected_category_id = int(selected_category_id)
            products = Product.objects.filter(category__id=selected_category_id, is_available=True)
        except ValueError:
            products = Product.objects.filter(is_available=True)
            selected_category_id = None
    else:
        products = Product.objects.filter(is_available=True)
        selected_category_id = None

    for product in products:
        badge_label = random.choice(list(badge_options.keys()))
        product.badge = badge_label
        product.badge_color = badge_options[badge_label]

    category_chunks = list(chunk_list(list(categories), 5))

    return render(request, 'home.html', {
        'products': products,
        'categories': categories,
        'category_chunks': category_chunks,
        'selected_category_id': selected_category_id,
        'category': featured_category,
        'category_products': products,
        'electronics_category': electronics_category,
        'electronics_products': electronics_products,
        'deals_category': deals_category,
        'deals_products': deals_products,
        'mens_category': mens_category,
        'mens_products': mens_products,
        'women_category': women_category,
        'women_products': women_products,
        'top_vendors': top_vendors,

    })
def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, is_available=True)

    badge_options = {
        'New': 'bg-primary',
        'Popular': 'bg-success',
        'Hot': 'bg-danger',
        'Trending': 'bg-warning text-dark',
        'Top': 'bg-dark'
    }

    for product in products:
        badge_label = random.choice(list(badge_options.keys()))
        product.badge = badge_label
        product.badge_color = badge_options[badge_label]

    return render(request, 'products/category_products.html', {
        'category': category,
        'products': products,
    })
    
def product_quick_view(request, pk):
    try:
        product = Product.objects.select_related('category', 'vendor', 'created_by').get(pk=pk)
        return JsonResponse({
            'name': product.name,
            'brand': product.brand,
            'category': product.category.name,
            'description': product.description or '',
            'base_price': str(product.base_price),
            'image': product.image.url if product.image else '',
            'rating': product.average_rating,
        })
    except Product.DoesNotExist:
        raise Http404("Product not found")  
def about_us(request):
    return render(request, 'about_us.html')
from django.shortcuts import redirect
from django.contrib import messages
from .models import Product, ProductQuestion

def submit_question(request):
    if request.method == 'POST':
        product_id = request.POST.get('product')
        email = request.POST.get('email')
        question_text = request.POST.get('question')

        try:
            product = Product.objects.get(id=product_id)
            ProductQuestion.objects.create(
                product=product,
                email=email,
                question=question_text
            )
            messages.success(request, "Your question has been submitted successfully.")
        except Product.DoesNotExist:
            messages.error(request, "Product not found.")

    return redirect(request.META.get('HTTP_REFERER', '/'))
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_protect

@csrf_protect
def ask_question(request):
    if request.method == "POST":
        product_name = request.POST.get("product_name")
        email = request.POST.get("email")
        question = request.POST.get("question")

        # Send email or store in DB
        send_mail(
            f"Product Inquiry: {product_name}",
            f"From: {email}\n\nQuestion:\n{question}",
            "no-reply@emarket.com",  # Your email
            ["support@emarket.com"],  # Support email
        )
        return redirect("product_detail") 
    from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Product, ProductQuestion

def ask_question(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        question_text = request.POST.get('question')
        email = request.POST.get('email')

        product = get_object_or_404(Product, id=product_id)

        # Save question to database
        ProductQuestion.objects.create(
            product=product,
            question=question_text,
            email=email
        )

        # Optional: send an email to site admin
        send_mail(
            subject=f"New Question about {product.name}",
            message=f"From: {email}\n\nQuestion:\n{question_text}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            fail_silently=True
        )

        messages.success(request, "Your question has been submitted successfully.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    messages.error(request, "Invalid request.")
    return redirect('/')
from django.shortcuts import render
from .models import Order
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

    return render(request, 'track_order.html', {'order': order, 'searched': searched})
def vendor_track_order_view(request):
    order = None
    searched = False

    if request.method == 'POST':
        query = request.POST.get('query')
        searched = True

        if query.isdigit():
            order = Order.objects.filter(id=query).first()
        else:
            order = Order.objects.filter(email__iexact=query).last()

    return render(request, 'vendor/track_order.html', {'order': order, 'searched': searched})
from django.shortcuts import render, get_object_or_404, redirect
from .models import CustomUser
from .forms import CustomerForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

def customer_list(request):
    query = request.GET.get('q')
    customers = CustomUser.objects.filter(is_customer=True)
    if query:
        customers = customers.filter(Q(username__icontains=query) | Q(email__icontains=query))
    paginator = Paginator(customers, 10)
    page = request.GET.get('page')
    customers = paginator.get_page(page)
    return render(request, 'admin/customers_list.html', {'customers': customers})

def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer created successfully.")
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'admin/customers_form.html', {'form': form, 'title': 'Add Customer'})

def customer_edit(request, pk):
    customer = get_object_or_404(CustomUser, pk=pk)
    form = CustomerForm(request.POST or None, request.FILES or None, instance=customer)
    if form.is_valid():
        form.save()
        messages.success(request, "Customer updated successfully.")
        return redirect('customer_list')
    return render(request, 'admin/customers_form.html', {'form': form, 'title': 'Edit Customer'})

def customer_delete(request, pk):
    customer = get_object_or_404(CustomUser, pk=pk)
    customer.delete()
    messages.success(request, "Customer deleted successfully.")
    return redirect('customer_list')
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Cart, CartItem, Product  # Adjust import as needed

@csrf_exempt
def update_cart_ajax(request):
    if request.method == 'POST' and request.user.is_authenticated:
        data = json.loads(request.body)
        item_id = data.get('id')
        action = data.get('action')

        try:
            cart = Cart.objects.get(user=request.user)
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return JsonResponse({'error': 'Cart item not found'}, status=404)

        if action == 'increase':
            cart_item.quantity += 1
            cart_item.save()
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
        elif action == 'remove':
            cart_item.delete()

        # Refresh cart data
        cart.refresh_from_db()
        cart_html = render_to_string('cart/ajax_cart_items.html', {'cart': cart})

        return JsonResponse({
            'cart_html': cart_html,
            'total_items': cart.total_items  # You must define this method/property
        })

    return JsonResponse({'error': 'Invalid request'}, status=400)
def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, is_available=True)
    return render(request, 'products/category_products.html', {
        'category': category,
        'products': products
    })
def vendor_detail(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    products = Product.objects.filter(vendor=vendor, is_available=True)

    # --- Filters ---
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    category_id = request.GET.get('category')
    sort = request.GET.get('sort')

    if min_price:
        products = products.filter(base_price__gte=min_price)
    if max_price:
        products = products.filter(base_price__lte=max_price)
    if category_id:
        products = products.filter(category__id=category_id)

    # --- Sorting ---
    if sort == 'price_low':
        products = products.order_by('base_price')
    elif sort == 'price_high':
        products = products.order_by('-base_price')
    elif sort == 'latest':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('name')  # Default sort

    # --- Social Links ---
    raw_links = [link.strip() for link in vendor.social_links.split(',')] if vendor.social_links else []
    social_links = []
    for link in raw_links:
        if 'facebook.com' in link:
            icon = 'fab fa-facebook'
        elif 'instagram.com' in link:
            icon = 'fab fa-instagram'
        elif 'twitter.com' in link:
            icon = 'fab fa-twitter'
        elif 'linkedin.com' in link:
            icon = 'fab fa-linkedin'
        elif 'youtube.com' in link:
            icon = 'fab fa-youtube'
        else:
            icon = 'fas fa-link'
        social_links.append({'url': link, 'icon': icon})

    # --- Category List for Filter Sidebar ---
    categories = Category.objects.all()

    return render(request, 'vendor/vendor_details.html', {
        'vendor': vendor,
        'social_links': social_links,
        'products': products,
        'categories': categories,
    })