from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from .models import Payment, Order, CustomUser, Vendor
from django.core.exceptions import ObjectDoesNotExist
import re

@login_required
def admin_payment_history(request):
    """
    View to display all payment records for admin with customer and vendor details.
    """
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')
    
    # Fetch payments with related order and user, and prefetch order items and their products' vendors
    payments = Payment.objects.select_related('order__user').prefetch_related('order__items__product__vendor').all().order_by('-order__created_at')
    latest_payment = payments.first() if payments.exists() else None
    
    context = {
        'payments': payments,
        'latest_payment': latest_payment,
    }
    return render(request, 'admin/payment_history.html', context)

@csrf_protect
@login_required
def admin_update_payment_method(request):
    """
    View to handle updating a payment method via AJAX.
    """
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)
    
    if request.method == 'POST':
        card_number = request.POST.get('card_number', '').replace(' ', '')
        expiry = request.POST.get('expiry', '')
        cvv = request.POST.get('cvv', '')
        
        # Basic validation
        if not card_number or not expiry or not cvv:
            return JsonResponse({'success': False, 'message': 'All fields are required.'}, status=400)
        
        # Validate card number (basic format check)
        if not re.match(r'^\d{12,19}$', card_number):
            return JsonResponse({'success': False, 'message': 'Invalid card number.'}, status=400)
        
        # Validate expiry format (MM/YY)
        if not re.match(r'^\d{2}/\d{2}$', expiry):
            return JsonResponse({'success': False, 'message': 'Invalid expiry date format. Use MM/YY.'}, status=400)
        
        # Validate CVV
        if not re.match(r'^\d{3,4}$', cvv):
            return JsonResponse({'success': False, 'message': 'Invalid CVV.'}, status=400)
        
        try:
            # Update the latest payment method
            payment = Payment.objects.select_related('order').latest('order__created_at')
            payment.card_number = card_number
            payment.expiry = expiry
            payment.cvv = cvv
            payment.save()
            
            return JsonResponse({'success': True, 'message': 'Payment method updated successfully.'})
        except ObjectDoesNotExist:
            return JsonResponse({'success': False, 'message': 'No payment method found.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)

@csrf_protect
@login_required
def admin_delete_payment_method(request):
    """
    View to handle deleting a payment method.
    """
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to perform this action.")
        return redirect('admin_payment_history')
    
    if request.method == 'POST':
        payment_id = request.POST.get('payment_id')
        try:
            payment = Payment.objects.get(id=payment_id)
            payment.delete()
            messages.success(request, "Payment method deleted successfully.")
        except ObjectDoesNotExist:
            messages.error(request, "Payment method not found.")
        except Exception as e:
            messages.error(request, f"Error deleting payment method: {str(e)}")
    
    return redirect('admin_payment_history')