# withdrawviews.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from .models import Vendor
from .forms import VendorBankForm

def is_admin(user):
    return user.is_staff or user.is_superuser

@user_passes_test(is_admin)
def vendor_withdrawal_preferences(request):
    query = request.GET.get('q', '')
    vendor_list = Vendor.objects.filter(business_name__icontains=query).order_by('-created_at')

    paginator = Paginator(vendor_list, 10)
    page_number = request.GET.get('page')
    vendors = paginator.get_page(page_number)

    return render(request, 'admin/withdrawal_method.html', {
        'vendors': vendors,
        'query': query
    })

@user_passes_test(is_admin)
def approve_vendor_payment_info(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    vendor.is_payment_info_verified = True
    vendor.save()
    messages.success(request, f"{vendor.business_name}'s bank details approved.")
    return redirect('vendor_withdrawal_preferences')

@user_passes_test(is_admin)
def reject_vendor_payment_info(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    vendor.is_payment_info_verified = False
    vendor.save()
    messages.warning(request, f"{vendor.business_name}'s bank details rejected.")
    return redirect('vendor_withdrawal_preferences')

@user_passes_test(is_admin)
def edit_vendor_bank_details(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    if request.method == 'POST':
        form = VendorBankForm(request.POST, instance=vendor)
        if form.is_valid():
            form.save()
            messages.success(request, f"{vendor.business_name}'s bank details updated.")
            return redirect('vendor_withdrawal_preferences')
    else:
        form = VendorBankForm(instance=vendor)
    return render(request, 'admin/edit_vendor_bank.html', {'form': form, 'vendor': vendor})

@user_passes_test(is_admin)
def delete_vendor_bank_details(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    vendor.bank_name = ''
    vendor.account_holder_name = ''
    vendor.account_number = ''
    vendor.swift_code = ''
    vendor.is_payment_info_verified = False
    vendor.save()
    messages.success(request, f"{vendor.business_name}'s bank details removed.")
    return redirect('vendor_withdrawal_preferences')
