# -*- coding: utf-8 -*-
from django.db import models

from django.template.loader import render_to_string
from django.utils.html import strip_tags
from premailer import transform
from django.core.mail import EmailMultiAlternatives

from directoalartista.apps.genericuser.models import GenericUser
from directoalartista.apps.artistprofile.models import ArtistProfile
from directoalartista.apps.invoicing.models import Invoice


class TransactionContact(models.Model):
    transaction_date = models.DateField(auto_now_add=True)
    proprietary_member = models.ForeignKey(GenericUser)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    vat = models.DecimalField(max_digits=10, decimal_places=2)
    gross_amount = models.DecimalField(max_digits=10, decimal_places=2)     # Total: price + vat
    bank_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    payment_complete = models.BooleanField(default=False)
    contact_provided = models.BooleanField(default=False)

    # Paypal
    paypal_ref = models.CharField(max_length=19)

    def send_contact(self):
        """
        Sends contact information to the member email address
        :return:
        """
        transitem = TransactionContactItem.objects.get(transaction=self)
        artist_profile = ArtistProfile.objects.get(id=transitem.artist_profile.id)
        user = transitem.transaction.proprietary_member
        contact = GenericUser.objects.get(id=artist_profile.proprietary_user.id)

        subject, from_email = 'Contacto de artista', 'Directo al Artista <info@directoalartista.com>'
        message = render_to_string('email/send_artist_contact.html', {
            'user': user, 'artist_profile': artist_profile, 'contact': contact,
        })

        html_content = render_to_string('email/global/template.html', {
            'email_title': 'Contacto de artista',
            'email_content': message,
        })

        html_content = transform(html_content)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(subject, text_content, from_email, [user.email])
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=True)

        self.contact_provided = True
        self.save()

        return True


class TransactionContactItem(models.Model):
    transaction = models.ForeignKey(TransactionContact, related_name='items', unique=False)
    artist_user = models.ForeignKey(GenericUser)
    artist_profile = models.ForeignKey(ArtistProfile, blank=True, null=True, on_delete=models.SET_NULL)
    item_id = models.CharField(max_length=10)
    description = models.CharField(max_length=100)
    unit_gross_amount = models.DecimalField(max_digits=10, decimal_places=2)     # Unit price + vat
    quantity = models.DecimalField(max_digits=8, decimal_places=2, default=1)

    def __unicode__(self):
        return self.description


class TransactionSubscription(models.Model):
    transaction_date = models.DateField(auto_now_add=True)
    proprietary_member = models.ForeignKey(GenericUser)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    vat = models.DecimalField(max_digits=10, decimal_places=2)
    gross_amount = models.DecimalField(max_digits=10, decimal_places=2)     # Total: price + vat
    bank_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    payment_complete = models.BooleanField(default=False)

    # Paypal
    paypal_ref = models.CharField(max_length=19)
    # For subscriptions only, paypal pass this for update or cancel plan
    paypal_profileid = models.CharField(max_length=20, blank=False)


class TransactionSubscriptionItem(models.Model):
    transaction = models.ForeignKey(TransactionSubscription, related_name='items', unique=False)
    item_id = models.CharField(max_length=10)
    description = models.CharField(max_length=100)
    unit_gross_amount = models.DecimalField(max_digits=10, decimal_places=2)     # Unit price + vat
    quantity = models.DecimalField(max_digits=8, decimal_places=2, default=1)

    def __unicode__(self):
        return self.description
