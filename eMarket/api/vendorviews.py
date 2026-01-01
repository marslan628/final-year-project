from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login
from .forms import UserForm, VendorForm

User = get_user_model()

from django.contrib import messages

def register_vendor(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        vendor_form = VendorForm(request.POST, request.FILES)
        if user_form.is_valid() and vendor_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.user_type = 'seller'
            user.save()

            vendor = vendor_form.save(commit=False)
            vendor.user = user
            vendor.save()

            login(request, user)
            messages.success(request, 'Registration successful! Welcome, vendor.')
            return redirect('home')  # replace with your actual dashboard route
    else:
        user_form = UserForm()
        vendor_form = VendorForm()

    return render(request, 'vendor/register.html', {
        'user_form': user_form,
        'vendor_form': vendor_form,
    })

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Vendor
from .forms import VendorForm
from django.contrib.auth.decorators import login_required, user_passes_test


def is_admin(user):
    return user.is_superuser


@login_required
@user_passes_test(is_admin)
def vendor_list(request):
    vendors = Vendor.objects.select_related('user').order_by('-created_at')
    return render(request, 'admin/vendor_list.html', {'vendors': vendors})


@login_required
@user_passes_test(is_admin)
def vendor_create(request):
    if request.method == 'POST':
        form = VendorForm(request.POST, request.FILES)
        if form.is_valid():
            vendor = form.save(commit=False)
            # Assign a user manually or redirect from User creation flow
            messages.success(request, 'Vendor created successfully.')
            return redirect('vendor_list')
    else:
        form = VendorForm()
    return render(request, 'admin/vendor_form.html', {'form': form, 'title': 'Create Vendor'})


@login_required
@user_passes_test(is_admin)
def vendor_edit(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    if request.method == 'POST':
        form = VendorForm(request.POST, request.FILES, instance=vendor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vendor updated successfully.')
            return redirect('vendor_list')
    else:
        form = VendorForm(instance=vendor)
    return render(request, 'admin/vendor_form.html', {'form': form, 'title': 'Edit Vendor'})


@login_required
@user_passes_test(is_admin)
def vendor_delete(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    if request.method == 'POST':
        vendor.delete()
        messages.success(request, 'Vendor deleted successfully.')
        return redirect('vendor_list')
    return render(request, 'admin/vendor_confirm_delete.html', {'vendor': vendor})

def vendor_detail(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    products = vendor.products.filter(is_available=True)

    return render(request, 'vendors/vendor_details.html', {
        'vendor': vendor,
        'products': products,
    })