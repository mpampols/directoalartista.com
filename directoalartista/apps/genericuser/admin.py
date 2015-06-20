# -*- coding: utf-8 -*-
from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from django.template.loader import render_to_string
from django.utils.html import strip_tags
from premailer import transform
from django.core.mail import EmailMultiAlternatives

from directoalartista.apps.genericuser.models import GenericUser
from directoalartista.apps.transaction.models import TransactionContact, TransactionContactItem,\
    TransactionSubscription, TransactionSubscriptionItem
from directoalartista.apps.artistprofile.models import ArtistProfile
from directoalartista.apps.plancontrol.backend import free_change_plan


def promoter_validation_accept(modeladmin, request, queryset):
    for user in queryset:
        transactions = TransactionContact.objects.filter(proprietary_member=user).filter(payment_complete=True)
        for trans in transactions:
            transitem = TransactionContactItem.objects.get(transaction=trans)
            artist_profile = ArtistProfile.objects.get(id=transitem.artist_profile.id)
            contact = GenericUser.objects.get(id=artist_profile.proprietary_user.id)

            # Send mail
            email = user.email
            subject, from_email = 'Contacto de artista', 'Directo al Artista <info@directoalartista.com>'
            message = render_to_string('email/promoter_validation_accepted.html', {
                'user': user, 'artist_profile': artist_profile, 'contact': contact,
            })
            html_content = render_to_string('email/global/template.html', {
                'email_title': 'Contacto de artista',
                'email_content': message,
            })
            html_content = transform(html_content)
            text_content = strip_tags(html_content)
            msg = EmailMultiAlternatives(subject, text_content, from_email, [email])
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=True)
        transactions.update(contact_provided=True)
    queryset.update(promoter_validated=True)
promoter_validation_accept.short_description = "Promoter validation: Accept"

def promoter_validation_refuse(modeladmin, request, queryset):
    queryset.update(promoter_validated=False)
    for user in queryset:
        # Send mail
        email = user.email
        subject, from_email = 'Necesitamos más datos para facilitarte el contacto', 'Directo al Artista <info@directoalartista.com>'
        message = render_to_string('email/promoter_validation_refused.html', {
            'user': user,
        })
        html_content = render_to_string('email/global/template.html', {
            'email_title': 'Necesitamos más datos para facilitarte el contacto',
            'email_content': message,
        })
        html_content = transform(html_content)
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(subject, text_content, from_email, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=True)
promoter_validation_refuse.short_description = "Promoter validation: Refuse"

def agency_validation_accepted(modeladmin, request, queryset):
    queryset.update(agency_validated=True)
    queryset.update(artist_plan='4')
    for user in queryset:
        # Send mail
        email = user.email
        subject, from_email = 'Solicitud de agencia aprobada', 'Directo al Artista <info@directoalartista.com>'
        message = render_to_string('email/agency_validation_accepted.html', {
            'user': user,
        })
        html_content = render_to_string('email/global/template.html', {
            'email_title': 'Solicitud de agencia aprobada',
            'email_content': message,
        })
        html_content = transform(html_content)
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(subject, text_content, from_email, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=True)
agency_validation_accepted.short_description = "Agency validation: Accept"

def agency_activation_refuse(modeladmin, request, queryset):
    queryset.update(agency_validated=False)
    for user in queryset:
        # Send mail
        email = user.email
        subject, from_email = 'Solicitud de agencia no aprobada', 'Directo al Artista <info@directoalartista.com>'
        message = render_to_string('email/agency_validation_refuse.html', {
            'user': user,
        })
        html_content = render_to_string('email/global/template.html', {
            'email_title': 'Solicitud de agencia no aprobada',
            'email_content': message,
        })
        html_content = transform(html_content)
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(subject, text_content, from_email, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=True)
agency_activation_refuse.short_description = "Agency validation: Refuse"

def agency_activation_change_to_promotor(modeladmin, request, queryset):
    queryset.update(agency_validated=False)
    queryset.update(promoter_validated=True)
    queryset.update(user_type='P')

    for user in queryset:
        # Change from agency to promotor values
        user.promoter_room_or_event_name = user.agency_name
        user.promoter_company_name = user.agency_company_name
        user.promoter_cif = user.agency_cif
        user.promoter_additional_info = user.agency_additional_info
        user.agency_name = user.agency_company_name = user.agency_cif = user.agency_additional_info = ''
        user.save()
        # Send mail
        email = user.email
        subject, from_email = 'Solicitud de agencia no aprobada, validado como promotor', 'Directo al Artista <info@directoalartista.com>'
        message = render_to_string('email/agency_activation_promoter_validated.html', {
            'user': user,
        })
        html_content = render_to_string('email/global/template.html', {
            'email_title': 'Solicitud de agencia no aprobada, validado como promotor',
            'email_content': message,
        })
        html_content = transform(html_content)
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(subject, text_content, from_email, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=True)
agency_activation_change_to_promotor.short_description = "Agency validation: Refuse, change to promotor"

def change_plan_to_free(modeladmin, request, queryset):
    for user in queryset:
        free_change_plan(user, '4')
        # Send mail
        email = user.email
        subject, from_email = 'Plan actualizado a Gratuito', 'Directo al Artista <noreply@directoalartista.com>'
        message = render_to_string('email/change_plan_to_free.html', {
            'user': user,
        })
        html_content = render_to_string('email/global/template.html', {
            'email_title': 'Vuelves a tener Plan Gratuito',
            'email_content': message,
        })
        html_content = transform(html_content)
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(subject, text_content, from_email, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=True)
change_plan_to_free.short_description = "Artist plan to: Free"

def change_plan_to_starter(modeladmin, request, queryset):
    for user in queryset:
        free_change_plan(user, '3')
        # Send mail
        email = user.email
        subject, from_email = 'Plan actualizado a Iniciado', 'Directo al Artista <noreply@directoalartista.com>'
        message = render_to_string('email/change_plan_to_starter.html', {
            'user': user,
        })
        html_content = render_to_string('email/global/template.html', {
            'email_title': 'Plan cambiado a Iniciado',
            'email_content': message,
        })
        html_content = transform(html_content)
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(subject, text_content, from_email, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=True)
change_plan_to_starter.short_description = "Artist plan to: Starter"

def change_plan_to_unlimited(modeladmin, request, queryset):
    for user in queryset:
        free_change_plan(user, '2')
        # Send mail
        email = user.email
        subject, from_email = 'Plan actualizado a Ilimitado', 'Directo al Artista <noreply@directoalartista.com>'
        message = render_to_string('email/change_plan_to_unlimited.html', {
            'user': user,
        })
        html_content = render_to_string('email/global/template.html', {
            'email_title': 'Plan cambiado a Ilimitado',
            'email_content': message,
        })
        html_content = transform(html_content)
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(subject, text_content, from_email, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=True)
change_plan_to_unlimited.short_description = "Artist plan to: Unlimited"


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = GenericUser
        fields = ('email',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = GenericUser
        exclude = []

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class GenericUserAdmin(UserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'first_name', 'last_name', 'user_type', 'artist_plan', 'date_joined')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Important dates', {'fields': ('date_joined', 'last_login',)}),
        ('Generic and artist fields', {'fields': ("first_name", "last_name", "dni", "phone", "address", "postal_code",
                                                  "city", "province", "user_type", "is_active",)}),
        ('Artist related fields', {'fields': ("artist_plan",)}),
        ('Promoter related fields', {'fields': ("promoter_company_name", "promoter_cif", "promoter_room_or_event_name",
                                                "promoter_additional_info", "promoter_validated",)}),
        ('Agency related fields', {'fields': ("agency_cif", "agency_company_name", "agency_name",
                                               "agency_additional_info", "agency_validated",)})
    )

    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
        ('Generic and artist fields', {'fields': ("first_name", "last_name", "dni", "phone", "address", "postal_code",
                                                  "city", "province", "user_type", "is_active",)}),
        ('Artist related fields', {'fields': ("artist_plan",)}),
        ('Promoter related fields', {'fields': ("promoter_company_name", "promoter_cif", "promoter_room_or_event_name",
                                                "promoter_additional_info", "promoter_validated",)}),
        ('Agency related fields', {'fields': ("agency_cif", "agency_company_name", "agency_name",
                                              "agency_additional_info", "agency_validated",)})
    )

    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    list_filter = ('user_type', 'artist_plan', 'is_active', 'promoter_validated', 'agency_validated',)
    filter_horizontal = ()
    actions = [promoter_validation_accept, promoter_validation_refuse,
               agency_validation_accepted, agency_activation_refuse, agency_activation_change_to_promotor,
               change_plan_to_free, change_plan_to_starter, change_plan_to_unlimited,
    ]


# Now register the new UserAdmin...
admin.site.register(GenericUser, GenericUserAdmin)
# ... and, since we're not using Django's builtin permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)