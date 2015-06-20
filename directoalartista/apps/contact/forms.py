# -*- coding: utf-8 -*-
from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={
            'class': 'form-control', 'placeholder': 'Nombre',
            'required': 'true'
        })
    )

    sender = forms.EmailField(max_length=50, widget=forms.TextInput(
        attrs={
            'class': 'form-control', 'placeholder': 'Correo electrónico',
            'required': 'true'
        })
    )

    phone = forms.CharField(
        required=False, max_length=15, widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Teléfono'}
        )
    )

    QUERYS = (
        ("", "Selecciona una opción"),
        ("general", "General"),
        ("comercial", "Comercial"),
        ("buscar artista", "No encuentro el artista que quiero"),
        ("facturacion", "Facturación"),
        ("webmaster", "Webmaster"),
    )

    typeofquery = forms.ChoiceField(choices=QUERYS, widget=forms.Select(
        attrs={'class': 'form-control', 'required': 'true'})
    )

    message = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'form-control', 'placeholder':
               'Escribe tu consulta', 'rows': '5', 'required': 'true'}
    ), max_length=2000)

    acceptpolicy = forms.BooleanField(required=True)
