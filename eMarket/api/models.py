from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils.text import slugify

# -------------------- Custom User Model --------------------
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_vendor = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.username


# -------------------- Vendor --------------------
class Vendor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='vendor', on_delete=models.CASCADE)
    vendor_slug = models.SlugField(blank=True, null=True)
    slug = models.SlugField(blank=True, null=True)
    business_name = models.CharField(max_length=255)
    business_type = models.CharField(max_length=100, choices=[
        ('Individual', 'Individual'),
        ('Company', 'Company'),
        ('Agency', 'Agency'),
    ])
    registration_number = models.CharField(max_length=100)
    tax_id = models.CharField(max_length=100, blank=True, null=True)
    business_description = models.TextField(blank=True)

    phone_number = models.CharField(max_length=20)
    alternate_phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    bank_name = models.CharField(max_length=100)
    account_holder_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=100)
    swift_code = models.CharField(max_length=100)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    available_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    business_license = models.FileField(upload_to='vendor/licenses/')
    tax_certificate = models.FileField(upload_to='vendor/tax_docs/', blank=True, null=True)
    id_proof = models.FileField(upload_to='vendor/id_proof/')
    logo = models.ImageField(upload_to='vendor/logos/', blank=True, null=True)

    website = models.URLField(blank=True, null=True)
    social_links = models.TextField(blank=True, help_text="Add links separated by commas")

    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_reviews = models.PositiveIntegerField(default=0)
    verified_vendor = models.BooleanField(default=False)

    preferred_payment_method = models.CharField(max_length=50, choices=[
        ('Bank Transfer', 'Bank Transfer'),
        ('PayPal', 'PayPal'),
    ])
    is_payment_info_verified = models.BooleanField(default=False)
    
    agreed_to_terms = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        if not self.vendor_slug:
            self.vendor_slug = slugify(self.business_name)
        super().save(*args, **kwargs)
    def __str__(self):
        return self.business_name

class Withdrawal(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    
    def __str__(self):
        return f"{self.vendor.business_name} - ${self.amount} - {self.status}"
# -------------------- Category --------------------
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='category_images/')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


# -------------------- Product --------------------
class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    short_details = models.TextField()
    description = models.TextField()
    brand = models.CharField(max_length=100, blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='products/')
    is_available = models.BooleanField(default=False)
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated tags")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, related_name="products")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="products_added")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum([r.rating for r in reviews]) / reviews.count(), 1)
        return 0

    def __str__(self):
        return self.name
class ProductQuestion(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="questions")
    email = models.EmailField()
    question = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    answered = models.BooleanField(default=False)

    def __str__(self):
        return f"Question on {self.product.name} by {self.email}"

# -------------------- Product Variants --------------------
class ProductColorVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='color_variants')
    color_name = models.CharField(max_length=50)
    color_code = models.CharField(max_length=7, blank=True, help_text='Hex code (e.g., #ff0000)')
    image = models.ImageField(upload_to='products/')
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - {self.color_name}"


class ProductSizeVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='size_variants')
    size_label = models.CharField(max_length=50)
    image = models.ImageField(upload_to='products/')
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - {self.size_label}"


# -------------------- Reviews --------------------
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')

    def __str__(self):
        return f'{self.user.username} - {self.product.name}'


# -------------------- Cart --------------------
from django.conf import settings
from django.db import models
from decimal import Decimal

class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = (
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    )

    code = models.CharField(max_length=20, unique=True)
    discount = models.DecimalField(max_digits=8, decimal_places=2)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES, default='percentage')
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_to = models.DateTimeField(null=True, blank=True)
    min_cart_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_uses = models.PositiveIntegerField(null=True, blank=True)
    uses_count = models.PositiveIntegerField(default=0)
    applicable_products = models.ManyToManyField('Product', blank=True)
    applicable_users = models.ManyToManyField('CustomUser', blank=True)

    def __str__(self):
        return self.code

    def is_valid_for_user(self, user):
        if self.applicable_users.exists() and user not in self.applicable_users.all():
            return False
        return True

    def is_expired(self):
        return self.expiry_date and timezone.now() > self.expiry_date

    def can_be_used(self):
        if not self.active or self.is_expired():
            return False
        if self.max_uses is not None and self.uses_count >= self.max_uses:
            return False
        return True

    def get_discount_amount(self, subtotal):
        if self.discount_type == 'percentage':
            return (self.discount / Decimal(100)) * subtotal
        return self.discount


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Cart ({self.user or 'Guest'})"

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.select_related('product', 'color', 'size'))

    def update_totals(self):
        subtotal = self.subtotal
        if self.coupon and self.coupon.can_be_used():
            if subtotal >= self.coupon.min_cart_amount:
                discount = self.coupon.get_discount_amount(subtotal)
                self.total = max(subtotal - discount, 0)
            else:
                self.total = subtotal
        else:
            self.total = subtotal
        self.save()

    def total_amount(self):
        return self.total

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @staticmethod
    def get_or_create_cart(request):
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user, session_key=None)
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            cart, _ = Cart.objects.get_or_create(user=None, session_key=session_key)
        return cart

    def merge_with(self, other_cart):
        for item in other_cart.items.all():
            existing_item = self.items.filter(
                product=item.product,
                color=item.color,
                size=item.size
            ).first()
            if existing_item:
                existing_item.quantity += item.quantity
                existing_item.save()
            else:
                item.cart = self
                item.save()
        other_cart.delete()
    def remove_coupon(self):
        self.coupon = None
        self.save()
        self.update_totals()

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    color = models.ForeignKey('ProductColorVariant', on_delete=models.SET_NULL, null=True, blank=True)
    size = models.ForeignKey('ProductSizeVariant', on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.product.name} in Cart ({self.cart.id})"

    @property
    def total_price(self):
        base_price = self.product.base_price
        color_price = self.color.price if self.color else Decimal(0)
        size_price = self.size.price if self.size else Decimal(0)
        return (base_price + color_price + size_price) * self.quantity
# -------------------- Order & Payment --------------------
from django.db import models
from django.utils import timezone
from datetime import timedelta

def default_estimated_delivery():
    return timezone.now().date() + timedelta(days=2)
class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
        ('Returned', 'Returned'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    # Shipment Info
    courier = models.CharField(max_length=100, blank=True, null=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    estimated_delivery = models.DateField(default=default_estimated_delivery, null=True, blank=True)
    def __str__(self):
        return f"Order #{self.id} - {self.status}"
    

   

    @property
    def progress(self):
        return {
            'Pending': 25,
            'Shipped': 50,
            'In Transit': 75,
            'Delivered': 100,
        }.get(self.status, 0)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.CharField(max_length=50, blank=True, null=True)
    size = models.CharField(max_length=50, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product} x {self.quantity}"


class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=20)  # Mask in production
    expiry = models.CharField(max_length=5)
    cvv = models.CharField(max_length=4)
    payment_status = models.CharField(max_length=20, default='Success')

    def __str__(self):
        return f"Payment for Order #{self.order.id}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=150)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"
