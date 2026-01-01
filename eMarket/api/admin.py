from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

admin.site.register(Category)
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1  # Number of empty forms to show by default

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'full_name', 'email', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'user')
    search_fields = ('full_name', 'email', 'phone')
    inlines = [OrderItemInline]

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'color', 'size', 'price', 'quantity')
    list_filter = ('order', 'product', 'color', 'size')

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'payment_status', 'card_number', 'expiry', 'cvv')
    list_filter = ('payment_status', 'order')
@admin.register(ProductQuestion)
class ProductQuestionAdmin(admin.ModelAdmin):
    list_display = ('product', 'email', 'created_at')
    search_fields = ('product__name', 'email', 'question')
# Register models with admin site
admin.site.register(Coupon)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Payment, PaymentAdmin)
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'base_price', 'stock', 'is_available', 'created_at', 'updated_at')
    list_filter = ('category', 'is_available')
    search_fields = ('name', 'category__name', 'brand')

@admin.register(ProductColorVariant)
class ProductColorVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'color_name', 'price', 'color_code')
    list_filter = ('product',)
    search_fields = ('color_name', 'product__name')

@admin.register(ProductSizeVariant)
class ProductSizeVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'size_label', 'price')
    list_filter = ('product',)
    search_fields = ('size_label', 'product__name')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('product__name', 'user__username')

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'user', 'phone_number', 'city', 'state', 'created_at')
    list_filter = ('city', 'state')
    search_fields = ('business_name', 'user__username', 'phone_number')

# Registering the CustomUser model with list_display
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        ("Additional Info", {
            "fields": ("phone", "profile_image", "is_vendor", "is_customer", "address")
        }),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_vendor', 'is_customer', 'is_active', 'last_login')
    list_filter = ('is_vendor', 'is_customer', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')

@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'amount', 'status', 'requested_at', 'processed_at']
    list_filter = ['status']
    actions = ['approve_withdrawals', 'reject_withdrawals']

    def approve_withdrawals(self, request, queryset):
        for withdrawal in queryset.filter(status='Pending'):
            withdrawal.status = 'Approved'
            withdrawal.processed_at = timezone.now()
            withdrawal.save()

    def reject_withdrawals(self, request, queryset):
        for withdrawal in queryset.filter(status='Pending'):
            withdrawal.status = 'Rejected'
            withdrawal.processed_at = timezone.now()
            withdrawal.vendor.available_balance += withdrawal.amount
            withdrawal.vendor.save()
            withdrawal.save()

    approve_withdrawals.short_description = "Approve selected withdrawals"
    reject_withdrawals.short_description = "Reject selected withdrawals"
admin.site.register(CustomUser, CustomUserAdmin)
