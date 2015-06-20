# -*- coding: utf-8 -*-
import math
from datetime import date
from io import BytesIO
from reportlab.pdfgen import canvas
from django.conf import settings

from django.db import models
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from premailer import transform
from django.core.mail import EmailMultiAlternatives

from directoalartista.apps.artistprofile.models import ArtistProfile
from directoalartista.apps.genericuser.models import GenericUser


class Invoice(models.Model):
    invoice_id = models.CharField(unique=True, max_length=8, null=False, blank=False)
    invoice_date = models.DateField(default=date.today)
    proprietary_member = models.ForeignKey(GenericUser)
    invoice_address = models.TextField(blank=False, null=False)
    sent = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    vat = models.DecimalField(max_digits=10, decimal_places=2)
    gross_amount = models.DecimalField(max_digits=10, decimal_places=2)     # Total: price + vat
    bank_fee = models.DecimalField(max_digits=10, decimal_places=2)     # Paypal or bank charges fee

    def file_name(self):
        """
        Generates the filename of the invoice
        :return:
        """
        return u'invoice-%s.pdf' % self.invoice_id

    def generate_pdf(self):
        """
        :return:
        """
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer)

        our_data = (
            'TRES NETWORK SCP',
            'CIF: J25747205',
            'Passeig de la Sardana, 15',
            '25230 Mollerussa (Lleida)',
        )
        invoice_address = self.invoice_address.split('\n')
        invoice_item = InvoiceItem.objects.get(invoice=self)
        vat = ((self.gross_amount/self.price) - 1) * 100
        vat = round(vat)

        # Draws the invoice header
        pdf.setFont('Helvetica-Bold', 12)
        pdf.drawInlineImage(settings.INVOICE_LOGO, 50, 700, width=190, height=60)
        textobject = pdf.beginText(300, 750)
        for line in our_data:
            textobject.textLine(line)
        pdf.drawText(textobject)

        # Draws the invoice customer info and invoice
        pdf.setFont('Helvetica', 12)
        textobject = pdf.beginText(300, 650)
        textobject.textLine('Num. factura: ' + self.invoice_id)
        textobject.textLine('Fecha: ' + self.invoice_date.strftime(settings.DATE_FORMAT))
        pdf.drawText(textobject)
        textobject = pdf.beginText(50, 650)
        for line in invoice_address:
            textobject.textLine(line)
        pdf.drawText(textobject)

        # Draws item and prices
        pdf.setFont('Helvetica-Bold', 12)
        pdf.drawString(50, 550, 'CONCEPTO')
        pdf.drawString(450, 550, 'PRECIO')
        pdf.line(50, 545, 500, 545)
        pdf.setFont('Helvetica', 12)
        pdf.drawString(50, 520, invoice_item.description)
        pdf.drawString(450, 520, str(round(self.price, 2)) + " €")
        pdf.drawString(50, 450, 'IVA ' + str(vat) + " %")
        pdf.drawString(450, 450, str(round(self.vat, 2)) + " €")
        pdf.setFont('Helvetica-Bold', 12)
        pdf.drawString(50, 430, 'TOTAL')
        pdf.drawString(450, 430, str(self.gross_amount) + " €")

        # Finish PDF
        pdf.showPage()
        pdf.save()
        pdf = buffer.getvalue()
        buffer.close()
        return pdf

    def send_invoice(self):
        """
        Sends a generated invoice to the members email address
        :return:
        """
        user = self.proprietary_member
        subject, from_email = 'Factura ' + self.invoice_id, 'Directo al Artista <noreply@directoalartista.com>'
        message = render_to_string('email/invoice_email.html', {'user': user,})

        html_content = render_to_string('email/global/template.html', {
            'email_title': 'Factura ' + self.invoice_id,
            'email_content': message,
        })
        html_content = transform(html_content)
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(subject, text_content, from_email, [user.email])
        msg.attach_alternative(html_content, "text/html")
        pdf = self.generate_pdf()
        msg.attach(self.file_name(), pdf, 'application/pdf')
        msg.send(fail_silently=True)

        self.sent = True
        self.save()
        return True

    def __unicode__(self):
        return self.invoice_id


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='items', unique=False)
    item_id = models.CharField(max_length=10)
    description = models.CharField(max_length=100)
    unit_gross_amount = models.DecimalField(max_digits=10, decimal_places=2)     # Unit price + vat
    quantity = models.DecimalField(max_digits=8, decimal_places=2, default=1)

    def __unicode__(self):
        return self.description
