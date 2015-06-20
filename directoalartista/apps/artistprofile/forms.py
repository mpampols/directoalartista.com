# -*- coding: utf-8 -*-
from django.forms import ModelForm
from django import forms
from django.contrib import *

from django.db import models

from django.contrib.admin.widgets import *

from djmoney.forms.fields import MoneyField

from django.contrib.auth import get_user_model
User = get_user_model()

from directoalartista.apps.artistprofile.models import  ArtistCategory, ArtistEventTypeCategory, ArtistPicture, \
    ArtistVideo, ArtistProfile, ArtistProvince

from djmoney.forms import MoneyWidget


class ArtistPictureForm(forms.Form):

    image = forms.ImageField(
        required=False,
        label='Select a file',
        help_text='max. 42 megabytes'
    )


class EditArtistPictureForm(ModelForm):

    artist_pictures = models.ForeignKey(ArtistPicture, unique=True)

    image = forms.ImageField(
        required=False,
        label='Select a file',
        help_text='max. 42 megabytes'
    )

    class Meta:
        model = ArtistPicture
        fields = '__all__'

    def save(self, commit=True):
        pass


class EditArtistVideoForm(ModelForm):

    artist_videos = models.ForeignKey(ArtistVideo, unique=True)

    video_url = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'required': 'true',
            'type': 'url',
        }),
                                    label='URL del vídeo',
    )

    class Meta:
        model = ArtistVideo
        fields = '__all__'

    def save(self, commit=True):
        pass


class ArtistProfileForm(forms.Form):
    artistic_name = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'required': 'true',
            'placeholder': "Ej: 'Ruben Poveda', 'Duo Mediterraneo - Orquesta'...",
        }),
                                    label='Nombre artístico',
    )

    category = forms.ChoiceField(widget=forms.Select(
        attrs={
            'class': 'form-control',
            'required': 'true'
        }),
                                 label='Categoría principal',
                                 choices=[(o.id, o) for o in ArtistCategory.objects.all()]
    )

    secondary_categories = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(
        attrs={
            'class': ''
        }),
                                                     required=False,
                                                     choices=[(o.id, o) for o in ArtistCategory.objects.all()]
    )

    event_type = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(
        attrs={
            'class': ''
        }),
                                                     choices=[(o.id, o) for o in ArtistEventTypeCategory.objects.all()]
    )

    provinces = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(
        attrs={
            'class': ''
        }),
                                         choices=[(o.id, o) for o in ArtistProvince.objects.all()]
    )

    min_price = forms.DecimalField(max_digits=12, decimal_places=0, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'type': 'number',
            'min': '0',
            'max': '999999',
            'step': 1,
        }),
                                label='Precio mínimo (Ej: 300)',
    )

    max_price = forms.DecimalField(max_digits=12, decimal_places=0, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'type': 'number',
            'min': '1',
            'max': '999999',
            'step': 1
        }),
                                label='Precio máximo (Ej: 1200)',
    )

    show_description = forms.CharField(max_length=1000, required=False, widget=forms.Textarea(
        attrs={
            'class': 'form-control',
        }),
                                             label='Descripción del espectáculo'
    )

    video1 = forms.URLField(max_length=100, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'type': 'url',
        }),
                                 required=False,
                                 label='Video URL'
    )

    is_vip = forms.BooleanField(required=False)


class EditArtistProfileForm(ModelForm):
    artist_profile = models.ForeignKey(ArtistProfile, unique=True)

    artistic_name = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'required': 'true'
        }),
                                    label='Nombre artístico',
    )

    category = forms.ModelChoiceField(widget=forms.Select(
        attrs={
            'class': 'form-control',
            'required': 'true'
        }),
                                      queryset=ArtistCategory.objects.all()
    )

    secondary_categories = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(
        attrs={
            'class': ''
        }),
                                                     required=False,
                                                     choices=[(o.id, o) for o in ArtistCategory.objects.all()]
    )

    event_type = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(
        attrs={
            'class': ''
        }),
                                                     choices=[(o.id, o) for o in ArtistEventTypeCategory.objects.all()]
    )

    provinces = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple(
        attrs={
            'class': ''
        }),
                                         queryset=ArtistProvince.objects.all()
    )

    min_price = forms.DecimalField(max_digits=12, decimal_places=0, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'type': 'number',
            'min': '0',
            'max': '999999',
            'step': 1
        }),
                                label='Precio mínimo (Ej: 300)',
    )

    max_price = forms.DecimalField(max_digits=12, decimal_places=0, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'type': 'number',
            'min': '1',
            'max': '999999',
            'step': 1
        }),
                                label='Precio máximo (Ej: 1200)',
    )

    show_description = forms.CharField(max_length=1000, required=False, widget=forms.Textarea(
        attrs={
            'class': 'form-control',
        }),
                                       label='Descripción del espectáculo'
    )

    video1 = forms.URLField(max_length=100, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'type': 'url',
        }),
                                 required=False,
                                 label='Video URL'
    )

    is_vip = forms.BooleanField(required=False)


class SearchCatalogForm(forms.Form):
    q = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': "Ej: 'Ruben Poveda', 'El Mecos de Aida'...",
        }),
                                    label='Búsqueda',
    )

    province = forms.ChoiceField(widget=forms.Select(
        attrs={
            'class': 'form-control'
        }),
        choices=[('0', 'Provincia')]+[(o.id, o) for o in ArtistProvince.objects.all()]
    )

    category = forms.ChoiceField(widget=forms.Select(
        attrs={
            'class': 'form-control',
        }),
        label='Categoría principal',
        choices=[('0', 'Categoría')]+[(o.id, o) for o in ArtistCategory.objects.all()]
    )

    event_type = forms.ChoiceField(widget=forms.Select(
        attrs={
            'class': 'form-control'
        }),
        choices=[('0', 'Tipo de evento')]+[(o.id, o) for o in ArtistEventTypeCategory.objects.all()]
    )

    PRICE_LIST = (
        ('0', 'Precio'),
        ('1', 'Gratuito'),
        ('2', 'Hasta 100€'),
        ('3', '101€ - 200€'),
        ('4', '201€ - 400€'),
        ('5', '401€ - 800€'),
        ('6', '801€ - 1.500€'),
        ('7', '1.501€ - 3.000€'),
        ('8', '3.001€ - 6.000€'),
        ('9', '6.001€ - 15.000€'),
        ('10', 'Más de 15.000€'),
    )

    price = forms.ChoiceField(widget=forms.Select(
        attrs={
            'class': 'form-control',
        }),
        choices=PRICE_LIST
    )