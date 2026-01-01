from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm

from django.core.mail import send_mail
from django.conf import settings

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()

            # Send email to admin
            send_mail(
                subject=f"New contact form message from {contact.name}",
                message=f"Subject: {contact.subject}\n\nMessage:\n{contact.message}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[contact.email, settings.CONTACT_RECIPIENT_EMAIL],  # Send to both user and admin
                fail_silently=False,
            )


            messages.success(request, "Your message has been sent successfully.")
            return redirect('contact')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})
