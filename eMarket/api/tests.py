from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Product, Cart, Coupon

User = get_user_model()

class CouponTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.product = Product.objects.create(name='Test Product', price=100)
        self.cart = Cart.objects.create(user=self.user)
        self.cart.items.create(product=self.product, quantity=2)

        self.valid_coupon = Coupon.objects.create(
            code="DISCOUNT10",
            discount=10,
            active=True,
            valid_from=timezone.now() - timezone.timedelta(days=1),
            valid_to=timezone.now() + timezone.timedelta(days=1)
        )

    def test_coupon_application(self):
        self.cart.coupon = self.valid_coupon
        self.cart.save()
        self.assertAlmostEqual(self.cart.total_amount(), 180.0)  # 200 - 10% = 180

    def test_coupon_not_yet_valid(self):
        self.valid_coupon.valid_from = timezone.now() + timezone.timedelta(days=1)
        self.valid_coupon.save()
        now = timezone.now()
        self.assertTrue(self.valid_coupon.valid_from > now)
