

from .models import Cart 

from datetime import datetime

def add_year(request):
    return {'year': datetime.now().year}

def cart_total_items(request):
    cart = Cart.get_or_create_cart(request)
    return {'cart': cart}
