from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from .models import Vendor
from .models import OrderItem

@receiver(post_save, sender=Order)
def update_vendor_earnings(sender, instance, **kwargs):
    if instance.status == 'Delivered':
        for item in OrderItem.objects.filter(order=instance):
            vendor = item.product.vendor
            earnings = item.price * item.quantity
            vendor.total_earnings += earnings
            vendor.available_balance += earnings
            vendor.save()
