# -*- coding: utf-8 -*-
from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin

from django.contrib.contenttypes import generic

from categories.admin import CategoryBaseAdminForm, CategoryBaseAdmin

from directoalartista.apps.transaction.models import TransactionContact, TransactionContactItem, \
    TransactionSubscription, TransactionSubscriptionItem


class TransactionContactItemInline(admin.TabularInline):
    model = TransactionContactItem

class TransactionSubscriptionItemInline(admin.TabularInline):
    model = TransactionSubscriptionItem

class TransactionContactAdmin(admin.ModelAdmin):
    inlines = [TransactionContactItemInline]
    list_display = ('id', 'proprietary_member', 'transaction_date', 'gross_amount', 'payment_complete',
                    'contact_provided')
    list_filter = ('payment_complete', 'contact_provided')
    ordering = ('-id',)
    search_fields = ('proprietary_member__email', 'paypal_ref')

    class Meta:
        model = TransactionContact

class TransactionSubscriptionAdmin(admin.ModelAdmin):
    inlines = [TransactionSubscriptionItemInline]
    list_display = ('id', 'proprietary_member', 'transaction_date', 'gross_amount', 'payment_complete')
    list_filter = ('payment_complete',)
    ordering = ('-id',)
    search_fields = ('proprietary_member__email',)

    class Meta:
        model = TransactionSubscription


admin.site.register(TransactionContact, TransactionContactAdmin)
admin.site.register(TransactionSubscription, TransactionSubscriptionAdmin)
