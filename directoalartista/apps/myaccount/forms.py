# -*- coding: utf-8 -*-
from django.forms import ModelForm
from django.db import models
from django import forms

from django.contrib.admin.widgets import *
from localflavor.es.forms import ESProvinceSelect, ESIdentityCardNumberField, ESPostalCodeField, ESPhoneNumberField
from directoalartista.apps.genericuser.models import GenericUser

from django.contrib.auth import get_user_model
User = get_user_model()


class GenericUserEditProfileFormArtist(ModelForm):

    user = models.ForeignKey(User, unique=True)

    email = forms.CharField(max_length=75, widget=forms.TextInput(
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

    actual_password = forms.CharField(max_length=60, required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'type': 'password',
        }),
                               label='Contraseña'
    )

    new_password = forms.CharField(max_length=60, required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'type': 'password',
        }),
                               label='Nueva contraseña'
    )

    new_password_repeat = forms.CharField(max_length=60, required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'type': 'password',
        }),
                               label='Repite la nueva contraseña'
    )

    newsletter_subscription = forms.BooleanField(required=False)

    class Meta:
        model = GenericUser
        fields = {"email", "phone", "first_name", "last_name", "dni", "address", "postal_code", "city", "province",
                  "actual_password", "new_password", "new_password_repeat", "newsletter_subscription"}

    def __unicode__(self):
        return unicode(self.user)

class GenericUserEditProfileFormAgency(ModelForm):

    user = models.ForeignKey(User, unique=True)

    email = forms.CharField(max_length=75, widget=forms.TextInput(
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

    agency_name = forms.CharField(max_length=255, required=True, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'required': 'true',
        }),
                                   label='Nombre de la agencia'
    )

    agency_company_name = forms.CharField(max_length=255, required=True, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'required': 'true',
        }),
                                           label='Razón social'
    )

    agency_cif = forms.CharField(max_length=15, required=True, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'required': 'true',
        }),
                                           label='CIF'
    )

    agency_additional_info = forms.CharField(max_length=1000, required=False, widget=forms.Textarea(
        attrs={
            'class': 'form-control',
            'required': 'false'
        }),
                                             label='Información adicional'
    )

    actual_password = forms.CharField(max_length=60, required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'type': 'password',
        }),
                               label='Contraseña'
    )

    new_password = forms.CharField(max_length=60, required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'type': 'password',
        }),
                               label='Nueva contraseña'
    )

    new_password_repeat = forms.CharField(max_length=60, required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'type': 'password',
        }),
                               label='Repite la nueva contraseña'
    )

    newsletter_subscription = forms.BooleanField(required=False)

    class Meta:
        model = GenericUser
        fields = {"email", "phone", "first_name", "last_name", "dni", "address", "postal_code", "city", "province",
                  "agency_additional_info", "agency_cif", "agency_company_name", "agency_name", "actual_password",
                  "new_password", "new_password_repeat", "newsletter_subscription"}

    def __unicode__(self):
        return unicode(self.user)

class GenericUserEditProfileFormPromoter(ModelForm):

    user = models.ForeignKey(User, unique=True)

    email = forms.CharField(max_length=75, widget=forms.TextInput(
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

    promoter_room_or_event_name = forms.CharField(max_length=255, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'required': 'true'
        }),
                                   label='Nombre de la sala o evento*'
    )

    promoter_company_name = forms.CharField(max_length=255, required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
        }),
                                           label='Razón social'
    )

    promoter_cif = forms.CharField(max_length=15, required=False, widget=forms.TextInput(
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

    actual_password = forms.CharField(max_length=60, required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'type': 'password',
        }),
                               label='Contraseña'
    )

    new_password = forms.CharField(max_length=60, required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'type': 'password',
        }),
                               label='Nueva contraseña'
    )

    new_password_repeat = forms.CharField(max_length=60, required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'type': 'password',
        }),
                               label='Repite la nueva contraseña'
    )

    newsletter_subscription = forms.BooleanField(required=False)

    class Meta:
        model = GenericUser
        fields = {"email", "phone", "first_name", "last_name", "dni", "address", "postal_code", "city", "province",
                  "promoter_room_or_event_name", "promoter_company_name", "promoter_cif", "promoter_additional_info",
                  "actual_password", "new_password", "new_password_repeat", "newsletter_subscription"}

    def __unicode__(self):
        return unicode(self.user)
