from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django.contrib.auth import get_user_model
User = get_user_model()
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Register'))

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('confirm_password'):
            self.add_error('confirm_password', "Passwords do not match.")
class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        exclude = ['created_at','user','is_payment_info_verified']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.label_class = 'fw-bold'
        self.helper.add_input(Submit('submit', 'Complete Registration'))
class BuyerSignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Sign Up'))

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'buyer'
        if commit:
            user.save()
        return user

class SellerSignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Register as Seller'))

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'seller'
        if commit:
            user.save()
        return user
from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
from django import forms
from .models import ContactMessage

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5}),
        }
from django import forms
from .models import CustomUser
from PIL import Image

class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'address', 'profile_image']
        widgets = {
            'email': forms.EmailInput(attrs={'readonly': 'readonly'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)

        if self.cleaned_data.get('profile_image'):
            image = self.cleaned_data['profile_image']
            img = Image.open(image)
            img = img.convert('RGB')
            img = img.resize((300, 300))  # Resize to 300x300
            img.save(user.profile_image.path)

        if commit:
            user.save()
        return user
from django import forms
from .models import Product, ProductColorVariant, ProductSizeVariant

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'short_details', 'description', 'brand', 'base_price', 'stock', 'image', 'tags']

class ProductColorVariantForm(forms.ModelForm):
    class Meta:
        model = ProductColorVariant
        fields = ['color_name', 'color_code', 'image', 'price']

class ProductSizeVariantForm(forms.ModelForm):
    class Meta:
        model = ProductSizeVariant
        fields = ['size_label', 'image', 'price']
class VendorBankForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['bank_name', 'account_holder_name', 'account_number', 'swift_code', 'preferred_payment_method']
        widgets = {
            'bank_name': forms.TextInput(attrs={'class': 'form-control'}),
            'account_holder_name': forms.TextInput(attrs={'class': 'form-control'}),
            'account_number': forms.TextInput(attrs={'class': 'form-control'}),
            'swift_code': forms.TextInput(attrs={'class': 'form-control'}),
            'preferred_payment_method': forms.Select(attrs={'class': 'form-select'}),
        }
class VendorProfileForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = [
            'business_name', 'business_type', 'registration_number', 'tax_id',
            'business_description', 'phone_number', 'alternate_phone',
            'address', 'city', 'state', 'zip_code', 'country',
            'bank_name', 'account_holder_name', 'account_number', 'swift_code',
            'preferred_payment_method', 'website', 'social_links', 'logo'
        ]
        widgets = {
            'business_description': forms.Textarea(attrs={'rows': 3}),
            'social_links': forms.Textarea(attrs={'rows': 2}),
        }
class ProductStockForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['stock']
        widgets = {
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }
class CustomerForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'address', 'profile_image', 'is_customer', 'is_active']
from django import forms
from .models import Coupon
from django.contrib.admin.widgets import AdminDateWidget
from django.forms.widgets import SelectDateWidget

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = [
            'code', 'discount', 'discount_type', 'min_cart_amount',
            'valid_from', 'valid_to', 'expiry_date', 'max_uses',
            'applicable_products', 'applicable_users', 'active'
        ]
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter coupon code'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control'}),
            'discount_type': forms.Select(attrs={'class': 'form-select'}),
            'min_cart_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'valid_from': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'valid_to': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'expiry_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'max_uses': forms.NumberInput(attrs={'class': 'form-control'}),
            'applicable_products': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'applicable_users': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
