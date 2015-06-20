from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.conf import settings

from forms import ContactForm
from django.core.mail import send_mail


def contact(request):
    if request.method == 'POST':  # If the form has been submitted...
        form = ContactForm(request.POST)  # A form bound to the POST data

        if form.is_valid():  # All validation rules pass
            sender = form.cleaned_data['sender']
            name = form.cleaned_data['name']
            phone = form.cleaned_data['phone']
            typeofquery = form.cleaned_data['typeofquery']
            messagetext = form.cleaned_data['message']

            if form.data['typeofquery'] == "facturacion":
                recipients = [settings.MAIL_ADMIN_INVOICE]
            elif form.data['typeofquery'] == "webmaster":
                recipients = [settings.MAIL_ADMIN_WEB]
            else:
                recipients = [settings.MAIL_INFO]

            subject = typeofquery + " | " + name

            message = "Name: " + name + "\nEmail: " + sender + \
                "\nPhone: " + phone + "\nMissatge: " + messagetext

            send_mail(subject, message, sender,
                      recipients, fail_silently=False)

            acceptpolicy = form.cleaned_data['acceptpolicy']

            # Redirect after POST
            return HttpResponseRedirect('/contact/sent/')
    else:
        form = ContactForm()  # An unbound form
    return render(request, 'contact.html', {
        'form': form,
    })
