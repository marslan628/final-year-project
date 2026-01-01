from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from .forms import UserForm, VendorForm
from django.contrib.auth.forms import AuthenticationForm
from .models import *
import random
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.views import (
    PasswordChangeView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)
User = get_user_model()

def register_customer(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            subject = 'Activate your eMarket account'
            message = render_to_string('auth/email_verification.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

            messages.success(request, 'Customer account created. Check your email to activate.')
            return redirect('login')
    else:
        user_form = UserForm()

    return render(request, 'auth/register_customer.html', {'user_form': user_form})


def register_vendor(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        vendor_form = VendorForm(request.POST, request.FILES)

        if user_form.is_valid() and vendor_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.is_active = False
            user.save()

            vendor = vendor_form.save(commit=False)
            vendor.user = user
            vendor.save()

            current_site = get_current_site(request)
            subject = 'Activate your eMarket Vendor Account'
            message = render_to_string('auth/email_verification.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

            messages.success(request, 'Vendor account created. Check your email to activate.')
            return redirect('login')
    else:
        user_form = UserForm()
        vendor_form = VendorForm()

    return render(request, 'auth/register_vendor.html', {
        'user_form': user_form,
        'vendor_form': vendor_form
    })


def chunk_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def home(request):
    selected_category_id = request.GET.get('category')
    categories = Category.objects.all()

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
    })


from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User as DjangoUser  # fallback if you're using default User

def login_view(request):
    if request.method == 'POST':
        identifier = request.POST.get('username')  # can be username or email
        password = request.POST.get('password')

        # Try authenticating by username first
        user = authenticate(request, username=identifier, password=password)

        # If not found, try treating identifier as email
        if user is None:
            try:
                user_obj = User.objects.get(email__iexact=identifier)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if user is not None:
            if user.is_active:
                login(request, user)

                # --- Cart Merging Logic ---
                session_key = request.session.session_key or request.session.create()
                guest_cart = Cart.objects.filter(session_key=session_key, user=None).first()
                user_cart, _ = Cart.objects.get_or_create(user=user, session_key=None)
                if guest_cart and guest_cart != user_cart:
                    user_cart.merge_with(guest_cart)

                messages.success(request, f"Welcome, {user.username}!")
                return redirect('home')
            else:
                messages.error(request, "Your account is inactive. Please check your email.")
        else:
            messages.error(request, "Invalid username/email or password.")
    return render(request, 'auth/login.html')


def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been activated. You can now log in.')
        return redirect('login')
    else:
        messages.error(request, 'Activation link is invalid or expired.')
        return redirect('login')


@login_required
def logout_view(request):
    auth_logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from .forms import ProfileForm

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('edit_profile')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'auth/edit_profile.html', {'form': form})

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'auth/change_password.html'
    success_url = reverse_lazy('edit_profile')

    def form_valid(self, form):
        messages.success(self.request, 'Your password was successfully updated!')

        user = self.request.user

        # Prepare email content
        subject = 'Password Change Confirmation'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = user.email

        context = {
            'username': user.get_full_name() or user.username,
            'support_email': 'support@emarket.pk',
            'site_name': 'eMarket.pk',
        }

        html_content = render_to_string('auth/email_password_changed.html', context)
        text_content = f"""
Hi {context['username']},

This is a confirmation that your password was successfully changed on {context['site_name']}.

If you did not make this change, please contact our support team immediately at {context['support_email']}.
"""

        # Send email
        email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        email.attach_alternative(html_content, "text/html")
        email.send()

        return super().form_valid(form)


class CustomPasswordResetView(PasswordResetView):
    template_name = 'auth/password_reset.html'
    email_template_name = 'emails/password_reset_email.html'
    subject_template_name = 'emails/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'auth/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'auth/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'auth/password_reset_complete.html'