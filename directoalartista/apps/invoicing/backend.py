# -*- coding: utf-8 -*-
from django.conf import settings
from datetime import date

from django.template.loader import render_to_string
from django.utils.html import strip_tags
from premailer import transform
from django.core.mail import EmailMultiAlternatives

from paypal.standard.ipn.signals import payment_was_successful, payment_was_flagged, payment_was_refunded,\
    subscription_cancel, subscription_signup, subscription_eot
from paypal.standard.forms import PayPalPaymentsForm

from directoalartista.apps.transaction.models import TransactionContact, TransactionContactItem,\
    TransactionSubscription, TransactionSubscriptionItem
from directoalartista.apps.invoicing.models import Invoice, InvoiceItem
from directoalartista.apps.artistprofile.models import ArtistProfile
from directoalartista.apps.plancontrol.backend import paypal_change_plan, paypal_subscription_canceled,\
    paypal_subscription_eot


def get_invoice_address(trans):
    if not trans.proprietary_member.address:
        trans.proprietary_member.address = ''
    if not trans.proprietary_member.postal_code:
        trans.proprietary_member.postal_code = ''
    if not trans.proprietary_member.city:
        trans.proprietary_member.city = ''

    if trans.proprietary_member.user_type == 'A':
        address = trans.proprietary_member.first_name + " " + trans.proprietary_member.last_name + "\n"\
                  + "DNI: " + trans.proprietary_member.dni + "\n"\
                  + trans.proprietary_member.address + "\n" + trans.proprietary_member.postal_code + " "\
                  + trans.proprietary_member.city + " (" + trans.proprietary_member.get_province_display() + ")"
    elif trans.proprietary_member.user_type == 'P':
        if not trans.proprietary_member.promoter_company_name:
            trans.proprietary_member.promoter_company_name = ''
        if not trans.proprietary_member.promoter_cif:
            trans.proprietary_member.promoter_cif = ''
        address = trans.proprietary_member.promoter_company_name + "\n"\
                  + "CIF: " + trans.proprietary_member.promoter_cif + "\n"\
                  + trans.proprietary_member.address + "\n" + trans.proprietary_member.postal_code + " "\
                  + trans.proprietary_member.city + " (" + trans.proprietary_member.get_province_display() + ")"
    elif trans.proprietary_member.user_type == 'G':
        if not trans.proprietary_member.agency_company_name:
            trans.proprietary_member.agency_company_name = ''
        if not trans.proprietary_member.agency_cif:
            trans.proprietary_member.agency_cif = ''
        address = trans.proprietary_member.agency_company_name + "\n"\
                  + "CIF: " + trans.proprietary_member.agency_cif + "\n"\
                  + trans.proprietary_member.address + "\n" + trans.proprietary_member.postal_code + " "\
                  + trans.proprietary_member.city + " (" + trans.proprietary_member.get_province_display() + ")"

    return address

def generate_invoice(trans, transitem):
    invoice = Invoice()
    if trans.gross_amount >= 0:
        # Normal Invoice, code DA-
        try:
            last_invoice = Invoice.objects.filter(invoice_id__startswith='DA-').order_by('id').reverse()[0]
            number = int(last_invoice.invoice_id[3:]) + 1
            invoice.invoice_id = "DA-" + str(number)
        except:
            invoice.invoice_id = "DA-1"
    else:
        # Refund Invoice, code DAR-
        try:
            last_invoice = Invoice.objects.filter(invoice_id__startswith='DAR-').order_by('id').reverse()[0]
            number = int(last_invoice.invoice_id[4:]) + 1
            invoice.invoice_id = "DAR-" + str(number)
        except:
            invoice.invoice_id = "DAR-1"

    invoice.invoice_date = date.today()
    invoice.proprietary_member = trans.proprietary_member
    invoice.invoice_address = get_invoice_address(trans)
    invoice.price = trans.price
    invoice.vat = trans.vat
    invoice.gross_amount = trans.gross_amount
    invoice.bank_fee = trans.bank_fee
    invoice.save()

    invoiceitem = InvoiceItem()
    invoiceitem.invoice = invoice
    invoiceitem.item_id = transitem.item_id
    invoiceitem.description = transitem.description
    invoiceitem.unit_gross_amount = transitem.unit_gross_amount
    invoiceitem.save()

    # Uncomment for send invoice
    # invoice.send_invoice()
    return invoice, invoiceitem

def payment_success(sender, **kwargs):
    ipn_obj = sender
    create_invoice = False
    if ipn_obj.txn_type == 'web_accept':
        trans = TransactionContact.objects.get(id=int(ipn_obj.invoice))
        transitem = TransactionContactItem.objects.get(transaction_id=trans.id)
        create_invoice = validate_payment(trans, transitem, ipn_obj)
    elif ipn_obj.txn_type == 'subscr_payment':
        trans = TransactionSubscription.objects.get(id=int(ipn_obj.invoice))
        transitem = TransactionSubscriptionItem.objects.get(transaction_id=trans.id)
        create_invoice = validate_payment(trans, transitem, ipn_obj)
    else:
        return False

    if create_invoice:
        trans.bank_fee = ipn_obj.mc_fee
        trans.payment_complete = True
        trans.save()
        invoice, invoiceitem = generate_invoice(trans, transitem)
        if ipn_obj.txn_type == 'web_accept':
            if trans.proprietary_member.user_type == 'P' and not trans.proprietary_member.promoter_validated:
                return mail_validate_promoter(trans, ipn_obj)
            else:
                return trans.send_contact()
        elif ipn_obj.txn_type == 'subscr_payment':
            return paypal_change_plan(invoice, invoiceitem, ipn_obj)

    return False

def payment_success_flagged(sender, **kwargs):
    ipn_obj = sender
    return False

def paypal_refund_payment(sender, **kwargs):
    ipn_obj = sender
    if ipn_obj.item_number[:2] == 'AC':
        trans = TransactionContact.objects.get(id=int(ipn_obj.invoice))
        transitem = TransactionContactItem.objects.get(transaction_id=trans.id)
    elif ipn_obj.item_number[:2] == 'SU':
        trans = TransactionSubscription.objects.get(id=int(ipn_obj.invoice))
        transitem = TransactionSubscriptionItem.objects.get(transaction_id=trans.id)
    else:
        return False

    trans.gross_amount = float(ipn_obj.mc_gross)
    trans.price = trans.gross_amount / (1 + settings.VAT_SPAIN)
    trans.vat = trans.gross_amount - trans.price
    trans.bank_fee = ipn_obj.mc_fee
    transitem.unit_gross_amount = trans.gross_amount
    transitem.description = "Devolucion factura: " + transitem.description

    return generate_invoice(trans, transitem)

def mail_validate_promoter(trans, ipn_obj):
    subject, from_email = 'DA admin - New promoter to validate', 'Directo al Artista <noreply@directoalartista.com>'
    message = render_to_string('email/payment_promoter_no_validated.html', {
        'user': trans.proprietary_member, 'artist_payed': ipn_obj.item_name,
    })

    html_content = render_to_string('email/global/template.html', {
        'email_title': 'New promoter to validate',
        'email_content': message,
    })

    html_content = transform(html_content)
    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(subject, text_content, from_email, ['info@directoalartista.com'])
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=True)

    return True

def validate_payment(trans, transitem, object):
    valid = True
    if settings.PAYPAL_RECEIVER_EMAIL != object.receiver_email:
        valid = False
    elif trans.gross_amount != object.mc_gross:
        valid = False
    elif object.mc_currency != 'EUR':
        valid = False
    elif transitem.description != object.item_name:
        valid = False
    elif transitem.item_id != object.item_number:
        valid = False

    return valid

def paypal_validate_plan_signup(sender, **kwargs):
    ipn_obj = sender
    valid = True
    trans = TransactionSubscription.objects.get(id=int(ipn_obj.invoice))

    if ipn_obj.period3 != '1 M':
        valid = False
    elif ipn_obj.recurring != '1':
        valid = False
    elif ipn_obj.mc_amount3 != trans.gross_amount:
        valid = False

    if not valid:
        subject, from_email = 'DA admin - Paypal subscription error', 'Directo al Artista <noreply@directoalartista.com>'
        message = render_to_string('email/paypal_subs_error.html', {
            'trans': trans, 'object': ipn_obj.item_name,
        })

        html_content = render_to_string('email/global/template.html', {
            'email_title': 'DA admin - Paypal subscription error',
            'email_content': message,
        })

        html_content = transform(html_content)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(subject, text_content, from_email, ['info@directoalartista.com'])
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=True)

    return valid

payment_was_successful.connect(payment_success)
payment_was_flagged.connect(payment_success_flagged)
payment_was_refunded.connect(paypal_refund_payment)

subscription_cancel.connect(paypal_subscription_canceled)
subscription_signup.connect(paypal_validate_plan_signup)
subscription_eot.connect(paypal_subscription_eot)