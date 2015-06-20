# -*- coding: utf-8 -*-
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from pyExcelerator import *

from directoalartista.apps.invoicing.models import Invoice, InvoiceItem


def export_as_xls(modeladmin, request, queryset):
    """
    Generic xls export admin action.
    """
    if not request.user.is_staff:
        raise PermissionDenied
    opts = modeladmin.model._meta

    wb = Workbook()
    ws0 = wb.add_sheet('0')
    col = 0
    field_names = []
    # write header row
    for field in opts.fields:
        ws0.write(0, col, field.name)
        field_names.append(field.name)
        col = col + 1

    row = 1
    # Write data rows
    for obj in queryset:
        col = 0
        for field in field_names:
            val = unicode(getattr(obj, field)).strip()
            ws0.write(row, col, val)
            col = col + 1
        row = row + 1

    wb.save('/tmp/output.xls')
    response = HttpResponse(open('/tmp/output.xls','r').read(),
                  mimetype='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=%s.xls' % unicode(opts).replace('.', '_')
    return response
export_as_xls.short_description = "Export selected invoices to XLS"

def resend_invoice(modeladmin, request, queryset):
    for i in queryset:
        i.send_invoice()
    queryset.update(sent=True)
resend_invoice.short_description = "Resend invoice"


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem

class InvoiceAdmin(admin.ModelAdmin):
    inlines = [InvoiceItemInline]
    list_display = ('id', 'invoice_id', 'proprietary_member', 'invoice_date', 'sent',)
    search_fields = ('invoice_id', 'proprietary_member__email',)
    ordering = ('-id',)
    list_filter = ('sent',)
    filter_horizontal = ()
    actions = [resend_invoice, export_as_xls,]


admin.site.register(Invoice, InvoiceAdmin)