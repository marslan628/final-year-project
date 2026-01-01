from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Order
import qrcode
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
import base64

def receipt_input_view(request):
    return render(request, 'receipt_input.html')

def generate_receipt(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # QR Code generation
    qr = qrcode.make(f'http://127.0.0.1:8000/track-order/{order.id}')
    qr_io = BytesIO()
    qr.save(qr_io, format='PNG')
    qr_base64 = base64.b64encode(qr_io.getvalue()).decode()
    qr_url = f'data:image/png;base64,{qr_base64}'

    # Barcode generation
    code128 = barcode.get('code128', str(order.id), writer=ImageWriter())
    bar_io = BytesIO()
    code128.write(bar_io)
    bar_base64 = base64.b64encode(bar_io.getvalue()).decode()
    bar_url = f'data:image/png;base64,{bar_base64}'

    return render(request, 'order_receipt.html', {
        'order': order,
        'qr_code_url': qr_url,
        'barcode_url': bar_url,
        'width': 58,  # or 58 for thermal printer
    })
