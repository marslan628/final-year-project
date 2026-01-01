from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib.admin.views.decorators import staff_member_required
from api.models import *
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product, Vendor
from django.shortcuts import redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from .models import Product
from .forms import *
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
import csv
from reportlab.pdfgen import canvas
from django.shortcuts import render
from .models import Withdrawal
def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def admin_dashboard(request):
    context = {
        "total_products": Product.objects.count(),
        "total_vendors": Vendor.objects.count(),
        "total_customers": CustomUser.objects.filter(is_vendor=False).count(),
        "pending_orders": Order.objects.filter(status='Pending').count(),
        "shipped_orders": Order.objects.filter(status='Shipped').count(),
        "delivered_orders": Order.objects.filter(status='Delivered').count(),
        "cancelled_orders": Order.objects.filter(status='Cancelled').count(),
    }
    return render(request, "admin/admin_dashboard.html", context)
@user_passes_test(is_admin)
def admin_product_list(request):
    vendor_id = request.GET.get('vendor')
    status = request.GET.get('status')

    products = Product.objects.all()

    if vendor_id:
        products = products.filter(vendor__id=vendor_id)
    if status == 'available':
        products = products.filter(is_available=True)
    elif status == 'unavailable':
        products = products.filter(is_available=False)

    total_products = products.count()
    available_products = products.filter(is_available=True).count()
    unavailable_products = total_products - available_products

    paginator = Paginator(products.order_by('-id'), 10)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)

    querystring = ''
    if vendor_id:
        querystring += f'&vendor={vendor_id}'
    if status:
        querystring += f'&status={status}'

    return render(request, 'admin/manage-products.html', {
        'page_obj': page_obj,
        'total_products': total_products,
        'available_products': available_products,
        'unavailable_products': unavailable_products,
        'vendors': Vendor.objects.all(),
        'filter_query': querystring
    })

@user_passes_test(is_admin)
def toggle_product_availability(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.is_available = not product.is_available
    product.save()
    return redirect(request.META.get('HTTP_REFERER', 'admin_product_list'))
@user_passes_test(is_admin)
def admin_edit_product(request, pk):
    if request.user.is_superuser or request.user.is_staff:
        product = get_object_or_404(Product, pk=pk)
    else:
        product = get_object_or_404(Product, pk=pk, created_by=request.user)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully.")
            return redirect('admin_product_list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'admin/edit_product.html', {
        'form': form,
        'title': 'Edit Product',
        'product': product
    })



from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
import csv



def admin_manage_orders(request):
    query = request.GET.get('q')
    status_filter = request.GET.get('status')
    export_csv = request.GET.get('export') == 'csv'

    orders = Order.objects.all().select_related('user').prefetch_related('items')

    # Search
    if query:
        orders = orders.filter(Q(full_name__icontains=query) | Q(email__icontains=query))

    # Filter by status
    if status_filter:
        orders = orders.filter(status=status_filter)

    # CSV Export
    if export_csv:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="orders.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Customer Name', 'Email', 'Total', 'Status', 'Created At'])

        for order in orders:
            writer.writerow([order.id, order.full_name, order.email, order.total_amount, order.status, order.created_at])
        return response

    # Pagination
    paginator = Paginator(orders.order_by('-created_at'), 10)
    page = request.GET.get('page')
    orders_page = paginator.get_page(page)

    context = {
        'orders': orders_page,
        'query': query,
        'status_filter': status_filter,
    }
    return render(request, 'admin/manage_orders.html', context)
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Order, OrderItem  # adjust if needed

# Only allow admin/staff users
@user_passes_test(lambda u: u.is_staff)
@login_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'mark_processing' and order.status == 'Pending':
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

        elif action == 'cancel_order' and order.status in ['Pending', 'Processing']:
            order.status = 'Cancelled'
            
            order.save()
            messages.success(request, "Order has been cancelled.")

        elif action == 'update_shipping':
            order.courier = request.POST.get('courier')
            order.tracking_number = request.POST.get('tracking_number')
            order.estimated_delivery = request.POST.get('estimated_delivery')
            order.save()
            messages.success(request, "Shipping information updated.")

        return redirect('admin_order_detail', order_id=order_id)

    return render(request, 'admin/order_detail.html', {
        'order': order,
        'order_items': order_items,
    })
def admin_vendor_withdrawals(request):
    withdrawals = Withdrawal.objects.select_related('vendor__user').all()
    return render(request, 'admin/admin_vendor_withdrawals.html', {'withdrawals': withdrawals})
from django.shortcuts import get_object_or_404, redirect, render
from .models import Withdrawal

def edit_withdrawal_view(request, pk):
    withdrawal = get_object_or_404(Withdrawal, pk=pk)
    
    if request.method == 'POST':
        withdrawal.bank_name = request.POST['bank_name']
        withdrawal.account_number = request.POST['account_number']
        withdrawal.amount = request.POST['amount']
        withdrawal.status = request.POST['status']
        withdrawal.save()
        
        messages.success(request, 'Withdrawal request updated successfully.')
        return redirect('admin_vendor_withdrawals')

    return render(request, 'admin/admin_edit_withdrawal.html', {'withdrawal': withdrawal})

def delete_withdrawal_view(request, pk):
    withdrawal = get_object_or_404(Withdrawal, pk=pk)
    
    # Deleting withdrawal request
    withdrawal.delete()
    
    messages.success(request, 'Withdrawal request deleted successfully.')
    return redirect('admin_vendor_withdrawals')

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.timezone import now

def approve_withdrawal_view(request, pk):
    withdrawal = get_object_or_404(Withdrawal, pk=pk)
    if withdrawal.status == 'Pending':
        withdrawal.status = 'Approved'
        withdrawal.save()

        # Email to vendor
        context = {
            'vendor': withdrawal.vendor,
            'amount': withdrawal.amount,
            'status': 'Approved',
            'timestamp': now(),
        }
        subject = f"[eMarket] Your withdrawal of PKR {withdrawal.amount:.2f} has been approved"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [withdrawal.vendor.user.email]
        text_content = (
            f"Dear {withdrawal.vendor.business_name},\n\n"
            f"Your withdrawal request of PKR {withdrawal.amount:.2f} has been approved.\n"
            f"Thank you for using eMarket."
        )
        html_content = render_to_string('emails/withdrawal_status_update.html', context)

        email = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
        email.attach_alternative(html_content, "text/html")
        email.send()

        messages.success(request, 'Withdrawal request approved successfully.')
    else:
        messages.warning(request, 'Withdrawal request is already processed.')
    return redirect('admin_vendor_withdrawals')

def reject_withdrawal_view(request, pk):
    withdrawal = get_object_or_404(Withdrawal, pk=pk)
    if withdrawal.status == 'Pending':
        withdrawal.status = 'Rejected'
        withdrawal.save()

        # Email to vendor
        context = {
            'vendor': withdrawal.vendor,
            'amount': withdrawal.amount,
            'status': 'Rejected',
            'timestamp': now(),
        }
        subject = f"[eMarket] Your withdrawal of PKR {withdrawal.amount:.2f} has been rejected"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [withdrawal.vendor.user.email]
        text_content = (
            f"Dear {withdrawal.vendor.business_name},\n\n"
            f"Your withdrawal request of PKR {withdrawal.amount:.2f} has been rejected.\n"
            f"Please contact support for more details."
        )
        html_content = render_to_string('emails/withdrawal_status_update.html', context)

        email = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
        email.attach_alternative(html_content, "text/html")
        email.send()

        messages.success(request, 'Withdrawal request rejected successfully.')
    else:
        messages.warning(request, 'Withdrawal request is already processed.')
    return redirect('admin_vendor_withdrawals')

def export_withdrawals_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="withdrawals.csv"'
    writer = csv.writer(response)
    writer.writerow(['Vendor', 'Amount', 'Status', 'Requested At'])

    for w in Withdrawal.objects.all():
        writer.writerow([w.vendor.business_name, w.amount, w.status, w.requested_at])

    return response

def export_withdrawals_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="withdrawals.pdf"'
    p = canvas.Canvas(response)
    p.drawString(100, 800, 'Withdrawal Requests')

    y = 780
    for w in Withdrawal.objects.all():
        line = f"{w.vendor.business_name} - PKR {w.amount} - {w.status}"
        p.drawString(100, y, line)
        y -= 20
        if y < 100:
            p.showPage()
            y = 800

    p.showPage()
    p.save()
    return response
from django.core.mail import send_mail
@user_passes_test(is_admin)
def admin_vendor_payment_list(request):
    vendors = Vendor.objects.all()
    return render(request, 'admin/vendor_payment_list.html', {'vendors': vendors})


@user_passes_test(is_admin)
def admin_edit_vendor_payment(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    if request.method == 'POST':
        form = VendorBankForm(request.POST, instance=vendor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vendor payment details updated successfully.')
            return redirect('admin_vendor_payment_list')
    else:
        form = VendorBankForm(instance=vendor)
    return render(request, 'admin/vendor_payment_edit.html', {'form': form, 'vendor': vendor})


@user_passes_test(is_admin)
def admin_delete_vendor_payment(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    vendor.delete()
    messages.success(request, 'Vendor payment method deleted.')
    return redirect('admin_vendor_payment_list')


@user_passes_test(is_admin)
def admin_approve_payment_info(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    vendor.is_payment_info_verified = True
    vendor.save()

    # Send email to vendor
    send_mail(
        subject='Your Payment Details Have Been Approved',
        message='Dear {},\n\nYour bank/payment details have been successfully approved.'.format(vendor.user.username),
        from_email='arslanirshad181@gmail.com',
        recipient_list=[vendor.user.email],
        fail_silently=False,
    )

    messages.success(request, 'Payment info approved and email sent to vendor.')
    return redirect('admin_vendor_payment_list')
@user_passes_test(is_admin)
def create_coupon(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coupon created successfully.')
            return redirect('admin-coupon-create')  # or to list page
    else:
        form = CouponForm()
    
    return render(request, 'admin/admin_coupon_create.html', {
        'form': form,
    })
from django.db.models import Q
from django.utils.dateparse import parse_date
@user_passes_test(is_admin)
def admin_coupon_list(request):
    coupons = Coupon.objects.all().order_by('-created_at')

    # Filters
    query = request.GET.get('q')
    status = request.GET.get('status')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if query:
        coupons = coupons.filter(code__icontains=query)

    if status == 'active':
        coupons = coupons.filter(active=True)
    elif status == 'inactive':
        coupons = coupons.filter(active=False)

    if start_date:
        coupons = coupons.filter(created_at__date__gte=parse_date(start_date))
    if end_date:
        coupons = coupons.filter(created_at__date__lte=parse_date(end_date))

    paginator = Paginator(coupons, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin/admin_coupon_list.html', {
        'coupons': page_obj,
        'query': query,
        'status': status,
        'start_date': start_date,
        'end_date': end_date
    })
@user_passes_test(is_admin)
def admin_coupon_edit(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    if request.method == 'POST':
        form = CouponForm(request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coupon updated successfully.')
            return redirect('admin_coupon_list')
    else:
        form = CouponForm(instance=coupon)
    return render(request, 'admin/admin_coupon_create.html', {'form': form})
    

@user_passes_test(is_admin)
def admin_coupon_delete(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    coupon.delete()
    messages.success(request, 'Coupon deleted successfully.')
    return redirect('admin_coupon_list')
from django.http import JsonResponse
from django.views.decorators.http import require_POST
@user_passes_test(is_admin)
@require_POST
def toggle_coupon_status(request):
    coupon_id = request.POST.get('id')
    coupon = get_object_or_404(Coupon, id=coupon_id)
    coupon.active = not coupon.active
    coupon.save()
    return JsonResponse({'success': True, 'new_status': coupon.active})