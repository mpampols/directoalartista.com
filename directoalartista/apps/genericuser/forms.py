# -*- coding: utf-8 -*-
from django.forms import ModelForm
from django import forms
from django.contrib import *
from django.contrib import admin
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator

from django.db import models

from django.contrib.admin.widgets import *

from localflavor.es.forms import ESProvinceSelect, ESIdentityCardNumberField, ESPostalCodeField, ESPhoneNumberField

from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from directoalartista.apps.genericuser.models import GenericUser

from django.contrib.auth import get_user_model
User = get_user_model()


class GenericUserCustomRegistrationFormPromoter(forms.Form):

    email = forms.EmailField(max_length=50, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'required': 'true',
            'type': 'email',
        }),
                            label='Email'
    )

    phone = ESPhoneNumberField(max_length=15, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'required': 'true',
            'type': 'tel',
        }),
                            label='Teléfono'
    )

    password1 = forms.CharField(max_length=60, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'required': 'true',
            'type': 'password',
        }),
                               label='Contraseña'
    )

    password2 = forms.CharField(max_length=60, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'required': 'true',
            'type': 'password',
        }),
                               label='Repite la contraseña'
    )

    first_name = forms.CharField(max_length=30, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'required': 'true'
        }),
                                 label='Nombre'
    )

    last_name = forms.CharField(max_length=60, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'required': 'true'
        }),
                                label='Apellidos'
    )

    dni = forms.CharField(max_length=10, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'required': 'true'
        }),
                          label='DNI'
    )

    address = forms.CharField(max_length=255, required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control'
        }),
                              label='Dirección'
    )

    postal_code = ESPostalCodeField(max_length=10, required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
        }),
                                label='Código postal'
    )

    city = forms.CharField(max_length=80, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'required': 'true'
        }),
                           label='Ciudad'
    )

    province = forms.CharField(max_length=80, widget=ESProvinceSelect(
        attrs={
            'class': 'form-control',
        }),
                               label='Provincia'
    )

    promoter_room_or_event_name = forms.CharField(max_length=255, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'required': 'true'
        }),
                                   label='Nombre de la sala o evento'
    )

    promoter_company_name = forms.CharField(max_length=255, required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
        }),
                                           label='Razón social'
    )

    promoter_cif = ESIdentityCardNumberField(required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
        }),
                                           label='CIF'
    )

    promoter_additional_info = forms.CharField(max_length=1000, required=False, widget=forms.Textarea(
        attrs={
            'class': 'form-control',
        }),
                                             label='Provincia'
    )

    newsletter_subscription = forms.BooleanField(initial=True, required=False)

    accept_tos = forms.BooleanField(
        error_messages={'required': 'Debes aceptar las condiciones de uso para poder registrarte'},
        label="Acepto las condiciones de uso."
    )


class GenericUserCustomRegistrationFormAgency(forms.Form):

    email = forms.EmailField(max_length=50, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'required': 'true',
            'type': 'email',
        }),
                            label='Email'
    )

    phone = ESPhoneNumberField(max_length=15, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'required': 'true',
            'type': 'tel',
        }),
                            label='Teléfono'
    )

    password1 = forms.CharField(max_length=60, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'required': 'true',
            'type': 'password',
        }),
                               label='Contraseña'
    )

    password2 = forms.CharField(max_length=60, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'required': 'true',
            'type': 'password',
        }),
                               label='Repite la contraseña'
    )

    first_name = forms.CharField(max_length=30, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'required': 'true'
        }),
                                 label='Nombre'
    )

    last_name = forms.CharField(max_length=60, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'required': 'true'
        }),
                                label='Apellidos'
    )

    dni = forms.CharField(max_length=10, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'required': 'true'
        }),
                          label='DNI'
    )

    address = forms.CharField(max_length=255, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'required': 'true'
        }),
                              label='Dirección'
    )

    postal_code = ESPostalCodeField(max_length=10, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'required': 'true'
        }),
                                  label='Código postal'
    )

    city = forms.CharField(max_length=80, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'required': 'true'
        }),
                           label='Ciudad'
    )

    province = forms.CharField(max_length=80, widget=ESProvinceSelect(
        attrs={
            'class': 'form-control',
        }),
                               label='Provincia'
    )

    agency_name = forms.CharField(max_length=255, required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'required': 'true'
        }),
                                   label='Nombre de la agencia'
    )

    agency_company_name = forms.CharField(max_length=255, required=True, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'required': 'true'
        }),
                                           label='Razón social'
    )

    agency_cif = ESIdentityCardNumberField(widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'required': 'true'
        }),
                                           label='CIF'
    )

    agency_additional_info = forms.CharField(max_length=1000, required=False, widget=forms.Textarea(
        attrs={
            'class': 'form-control',
        }),
                                             label='Información adicional'
    )

    newsletter_subscription = forms.BooleanField(initial=True, required=False)

    accept_tos = forms.BooleanField(
        error_messages={'required': 'Debes aceptar las condiciones de uso para poder registrarte'},
        label="Acepto las condiciones de uso."
    )

class GenericUserCustomRegistrationFormArtist(forms.Form):

    email = forms.EmailField(max_length=50, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'required': 'true',
            'type': 'email',
        }),
                            label='Email'
    )

    phone = ESPhoneNumberField(max_length=15, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'required': 'true',
            'type': 'tel',
        }),
                            label='Teléfono'
    )

    password1 = forms.CharField(max_length=60, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'required': 'true',
            'type': 'password',
        }),
                               label='Contraseña'
    )

    password2 = forms.CharField(max_length=60, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'required': 'true',
            'type': 'password',
        }),
                               label='Repite la contraseña'
    )

    first_name = forms.CharField(max_length=30, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'El de verdad, no el artístico',
            'required': 'true'
        }),
                                 label='Nombre'
    )

    last_name = forms.CharField(max_length=60, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'required': 'true'
        }),
                                label='Apellidos'
    )

    dni = forms.CharField(max_length=10, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'required': 'true'
        }),
                          label='DNI'
    )

    address = forms.CharField(max_length=255, required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control'
        }),
                              label='Dirección'
    )

    postal_code = ESPostalCodeField(max_length=10, required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
        }),
                                  label='Código postal'
    )

    city = forms.CharField(max_length=80, required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
        }),
                           label='Ciudad'
    )

    province = forms.CharField(max_length=80, widget=ESProvinceSelect(
        attrs={
            'class': 'form-control',
        }),
                               label='Provincia'
    )

    newsletter_subscription = forms.BooleanField(initial=True, required=False)

    accept_tos = forms.BooleanField(
        error_messages={'required': 'Debes aceptar las condiciones de uso para poder registrarte'},
        label="Acepto las condiciones de uso."
    )

    def clean_phone(self):
        """ Empty not allowed """

        data = self.cleaned_data['phone']
        if not data.strip():
            raise forms.ValidationError("Please enter your phone")

        return data

    def save(self, profile_callback=None):
        new_user = RegistrationProfile.objects.create_inactive_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password1'],
            email=self.cleaned_data['email'])

        new_profile = Profile(user=new_user,
                              phone=self.cleaned_data['phone'],
                              )
        new_profile.save()

        return new_user

    class Meta:
        model = GenericUser


class CustomPasswordResetForm(PasswordResetForm):
    """
        Overriding the Email Password Resert Forms Save to be able to send HTML email
        Test for send with template on /email/global/template
    """
    def save(self, domain_override=None, email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator, request=None, email_subject_name='registration/password_reset_subject.txt', **kwargs):
        from django.core.mail import EmailMultiAlternatives
        from django.utils.html import strip_tags
        from django.template.loader import render_to_string
        from django.contrib.sites.models import get_current_site
        from django.utils.http import int_to_base36
        from premailer import transform

        for user in self.users_cache:
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                 site_name = domain = domain_override

            subject, from_email = 'Reiniciar contraseña', 'Directo al Artista <noreply@directoalartista.com>'
            message = render_to_string('email/password_reset_email.html', {
                'email': user.email,
                'domain': domain,
                'uid': int_to_base36(user.id),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': use_https and 'https' or 'http',
            })

            html_content = render_to_string('email/global/template.html', {
                'email_title': 'Reiniciar contraseña',
                'email_content': message,
                'domain': domain,
                'token': token_generator.make_token(user),
            })

            html_content = transform(html_content)
            text_content = strip_tags(html_content)

            msg = EmailMultiAlternatives(subject, text_content, from_email, [user.email])
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=True)


class ResendActivationEmailForm(forms.Form):
    email = forms.CharField(max_length=75, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'required': 'true'
        }),
                            label='Email'
    )
