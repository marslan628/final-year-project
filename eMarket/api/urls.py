from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from django.contrib.auth.views import LoginView, LogoutView
from . import  testcart, views,history, receipt,authviews, widthrawviews,vendorviews,adminviews, productsviews, cartviews, checkoutviews, contactviews, shopviews, userdashviews, paymentviews, vendashviews
from .productsviews import ProductListView, ProductDetailView, add_review, ajax_filter_products, add_to_cart, search_products
from .authviews import edit_profile, CustomPasswordChangeView

urlpatterns = [
    # -------------------- Authentication --------------------
    path('login/', authviews.login_view, name='login'),
    path('register/', authviews.register_customer, name='register_customer'),
    path('vendor/register', authviews.register_vendor, name='register_vendor'),
    path('logout/', authviews.logout_view, name='logout'),
    path('activate/<uidb64>/<token>/', authviews.activate_account, name='activate'),

    # -------------------- Vendor Authentication --------------------
    path('vendor/register/', vendorviews.register_vendor, name='register_seller'),

    # -------------------- Vendor Dashboard --------------------
    path('vendor/dashboard/', vendashviews.vendor_dashboard, name='vendor_dashboard'),
    path('vendor/payments/', vendashviews.payment_history, name='vendor_payment_history'),
    path('vendor/edit-profile/', vendashviews.edit_vendor_profile, name='edit_vendor_profile'),
    path('vendor/earnings/', vendashviews.vendor_earnings, name='vendor_earnings'),
    path('vendor/<int:vendor_id>/', vendorviews.vendor_detail, name='vendor_detail'),
    # -------------------- Vendor Product Management --------------------
    path('vendor/products/', vendashviews.product_dashboard, name='product_dashboard'),
    path('vendor/products/add/', vendashviews.add_product, name='add_product'),
    path('vendor/products/<int:pk>/edit/', vendashviews.edit_product, name='edit_product'),
    path('vendor/products/<int:pk>/delete/', vendashviews.delete_product, name='delete_product'),
    path('vendor/products/<int:product_id>/update-stock/', vendashviews.update_product_stock, name='update_product_stock'),

    # -------------------- Vendor Product Variants --------------------
    path('vendor/products/<int:product_id>/variants/', vendashviews.manage_variants, name='manage_variants'),
    path('vendor/products/<int:product_id>/variants/add_color/', vendashviews.add_color_variant, name='add_color_variant'),
    path('vendor/products/<int:product_id>/variants/add_size/', vendashviews.add_size_variant, name='add_size_variant'),
    path('products/<int:product_id>/variants/color/<int:variant_id>/edit/', vendashviews.edit_color_variant, name='edit_color_variant'),
    path('products/<int:product_id>/variants/color/<int:variant_id>/delete/', vendashviews.delete_color_variant, name='delete_color_variant'),
    path('products/<int:product_id>/variants/size/<int:variant_id>/edit/', vendashviews.edit_size_variant, name='edit_size_variant'),
    path('products/<int:product_id>/variants/size/<int:variant_id>/delete/', vendashviews.delete_size_variant, name='delete_size_variant'),

    # -------------------- Vendor Order Management --------------------
    path('vendor/orders/', vendashviews.manage_orders, name='vendor_manage_orders'),
    path('vendor/orders/<int:order_id>/', vendashviews.vendor_order_detail, name='vendor_order_detail'),
    path('vendor/order-history/', vendashviews.order_history, name='vendor_order_history'),
    path('vendor/payment-details/', vendashviews.vendor_payment_details, name='vendor_payment_details'),
    path('vendor/<slug:vendor_slug>/', views.vendor_detail, name='vendor_detail'),

    # -------------------- Products --------------------
    path('search/', search_products, name='search_products'),
    path('product/', ProductListView.as_view(), name='product_list'),
    path('products/quick-view/<int:product_id>/', productsviews.quick_view, name='quick_view'),
    path('category/<slug:slug>/', views.category_products, name='category_products'),
    path('category/quick-view/<int:pk>/', views.product_quick_view, name='product_quick_view'),
    path('ajax/filter-products/', ajax_filter_products, name='ajax_filter_products'),
    path('product/category/<slug:slug>/', ProductListView.as_view(), name='product_list_by_category'),
    path('product/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('product/<slug:slug>/review/', add_review, name='add_review'),

    # -------------------- Cart --------------------
    path('cart/', cartviews.cart_view, name='cart_view'),
    path('cart/add/', testcart.add_to_cart, name='add_to_cart'),
    path('cart/add/', cartviews.add_to_cart, name='add_to_cart'),
    path('cart/add/<int:product_id>/', cartviews.add_to_cart, name='add_to_cart'),
    path('cart/apply-coupon/', cartviews.apply_coupon, name='apply_coupon'),
    path('ajax/update-cart/', views.update_cart_ajax, name='update_cart_ajax'),
    path('cart', cartviews.cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', cartviews.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', cartviews.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', cartviews.remove_cart_item, name='remove_cart_item'),
    path('cart/apply-coupon/', cartviews.apply_coupon, name='apply_coupon'),
    path('cart/remove-coupon/', cartviews.remove_coupon, name='remove_coupon'),
    # -------------------- Checkout --------------------
    path('checkout/', checkoutviews.checkout_view, name='checkout'),
    path('order/confirmation/<int:order_id>/', checkoutviews.order_confirmation, name='order_confirmation'),

  
    # -------------------- Static Pages --------------------
    path('', views.home, name='home'),
    path('shop/', shopviews.shop_view, name='shop'),
    path('contact/', contactviews.contact_view, name='contact'),
    path('about/', views.about_us, name='about_us'),
    path('submit-question/', views.submit_question, name='submit_question'),
    path('ask-question/', views.ask_question, name='ask_question'),

    # -------------------- Track Orders --------------------
    path('track-order/', views.track_order_view, name='track_order'),
    path('vendor/vendor-track-order/', views.vendor_track_order_view, name='vendor_track_order_view'),

    # -------------------- Customer Dashboard --------------------
    path('dashboard/', userdashviews.customer_dashboard, name='customer_dashboard'),
    path('order-history/', userdashviews.order_history, name='order_history'),
    path('order/<int:order_id>/', userdashviews.order_detail, name='order_detail'),
    path('my-orders/', userdashviews.my_orders, name='my_orders'),
    path('track-orders/', userdashviews.track_order_view, name='track_order_view'),
    path('orders/reorder/<int:order_id>/', userdashviews.reorder_view, name='reorder'),

    # -------------------- Payment --------------------
    path('payments/', paymentviews.payment_history, name='payment_history'),
    path('payments/delete/', paymentviews.delete_payment_method, name='delete_payment_method'),
    path('update-payment-method/', paymentviews.update_payment_method, name='update_payment_method'),
    path('receipt/<int:order_id>/', receipt.generate_receipt, name='generate_receipt'),
    path('receipt/', receipt.receipt_input_view, name='receipt_input'),
    path('admin-panel/payment-history/', history.admin_payment_history, name='admin_payment_history'),
    path('admin-panel/update-payment-method/', history.admin_update_payment_method, name='admin_update_payment_method'),
    path('admin-panel/delete-payment-method/', history.admin_delete_payment_method, name='admin_delete_payment_method'),
    # -------------------- Profile --------------------
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('profile/change-password/', CustomPasswordChangeView.as_view(), name='change_password'),

    # -------------------- Password Reset --------------------
    path('password-reset/', authviews.PasswordResetView.as_view(
        template_name='auth/password_reset.html',
        email_template_name='emails/password_reset_email.html',
        subject_template_name='emails/password_reset_subject.txt',
        success_url='/password-reset/done/'
    ), name='password_reset'),

    path('password-reset/done/', authviews.PasswordResetDoneView.as_view(
        template_name='auth/password_reset_done.html'
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', authviews.PasswordResetConfirmView.as_view(
        template_name='auth/password_reset_confirm.html',
        success_url='/reset/done/'
    ), name='password_reset_confirm'),

    path('reset/done/', authviews.PasswordResetCompleteView.as_view(
        template_name='auth/password_reset_complete.html'
    ), name='password_reset_complete'),
    #-------------Admin------------------------------------------
    path('admin-panel/', adminviews.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/dashboard', adminviews.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/products/', adminviews.admin_product_list, name='admin_product_list'),
    path('admin-panel/products/<int:pk>/toggle-availability/', adminviews.toggle_product_availability, name='toggle_product_availability'),
    path('admin-panel/products/<int:pk>/edit/', adminviews.admin_edit_product, name='admin_edit_product'),
    path('admin-panel/orders/', adminviews.admin_manage_orders, name='admin_manage_orders'),
    path('admin-panel/order/<int:order_id>/', adminviews.admin_order_detail, name='admin_order_detail'),
    path('admin-panel/coupons/create/', adminviews.create_coupon, name='admin-coupon-create'),
    path('admin-panel/coupons', adminviews.admin_coupon_list, name='admin_coupon_list'),
    path('admin-panel/coupons/edit/<int:coupon_id>/', adminviews.admin_coupon_edit, name='admin-coupon-edit'),
    path('admin-panel/coupons/delete/<int:coupon_id>/', adminviews.admin_coupon_delete, name='admin-coupon-delete'),
    path('admin/coupons/toggle-status/', adminviews.toggle_coupon_status, name='admin-coupon-toggle-status'),

    #-------------Admin-Withdraw-----------------------------
    path('admin-panel/withdrawals/', adminviews.admin_vendor_withdrawals, name='admin_vendor_withdrawals'),
    path('admin-panel/withdrawals/edit/<int:pk>/', adminviews.edit_withdrawal_view, name='admin_edit_withdrawal'),
    path('admin-panel/withdrawals/delete/<int:pk>/', adminviews.delete_withdrawal_view, name='admin_delete_withdrawal'),
    path('admin-panel/withdrawals/approve/<int:pk>/', adminviews.approve_withdrawal_view, name='admin_approve_withdrawal'),
    path('admin-panel/withdrawals/reject/<int:pk>/', adminviews.reject_withdrawal_view, name='admin_reject_withdrawal'),
    path('admin-panel/withdrawals/export/csv/', adminviews.export_withdrawals_csv, name='export_withdrawals_csv'),
    path('admin-panel/withdrawals/export/pdf/', adminviews.export_withdrawals_pdf, name='export_withdrawals_pdf'),
    path('admin-panel/vendor-withdrawal-methods/', widthrawviews.vendor_withdrawal_preferences, name='vendor_withdrawal_preferences'),
    path('admin-panel/vendor-withdrawal-methods/<int:vendor_id>/approve/', widthrawviews.approve_vendor_payment_info, name='approve_vendor_payment_info'),
    path('admin-panel/vendor-withdrawal-methods/<int:vendor_id>/reject/', widthrawviews.reject_vendor_payment_info, name='reject_vendor_payment_info'),
    path('admin-panel/vendor-withdrawal-methods/<int:vendor_id>/edit/',widthrawviews.edit_vendor_bank_details, name='edit_vendor_bank_details'),
    path('admin-panel/vendor-withdrawal-methods/<int:vendor_id>/delete/', widthrawviews.delete_vendor_bank_details, name='delete_vendor_bank_details'),
    #--------------------Admin---Vendors----------------------------------------------------
    path('admin-panel/vendors/', vendorviews.vendor_list, name='vendor_list'),
    path('admin-panel/vendors/create/', vendorviews.vendor_create, name='vendor_create'),
    path('admin-panel/vendors/<int:pk>/edit/', vendorviews.vendor_edit, name='vendor_edit'),
    path('admin-panel/vendors/<int:pk>/delete/', vendorviews.vendor_delete, name='vendor_delete'),
    #------------------------Customers-------CURD--------Admin----------------------------------
    path('admin-panel/customers/', views.customer_list, name='customer_list'),
    path('admin-panel/customers/add/', views.customer_create, name='customer_create'),
    path('admin-panel/customers/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('admin-panel/customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),
]

# -------------------- Static Media --------------------
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
