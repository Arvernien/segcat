from django import forms
from django.core.exceptions import ValidationError

from .models import Desconocido, actuaciones

class DesconocidoForm(forms.ModelForm):
    titular_candidato = forms.CharField(required=False, label="Titular candidato", widget=forms.TextInput({
        'class': 'form-control form-control-sm',
        'placeholder': 'Nombre y apellidos',

    }))
    nif_candidato = forms.CharField(required=False, label="NIF", widget=forms.TextInput({
        'class': 'form-control form-control-sm',
        'placeholder': 'NIF o CIF'
    }))
    telefono = forms.CharField(required=False, label="Teléfono", widget=forms.TextInput({
        'class': 'form-control form-control-sm',
        'placeholder': 'Número'
    }))
    mt = forms.BooleanField(required=False, label="Modificación de titular realizada", widget=forms.CheckboxInput({
        'class': 'toggle-btn',
        'onchange': "disablegestion();",
        'data-on': 'Sí',
        'data-off': 'No',
    }))
    expediente = forms.CharField(required=False, label="Titular candidato", widget=forms.TextInput({
        'class': 'form-control form-control-sm',
        'placeholder': 'Expediente gtt'
    }))
    liq = forms.BooleanField(required=False, label="Liquidación realizada", widget=forms.CheckboxInput({
        'class': 'toggle-btn',
        'onchange': "disableliq();",
        'data-on': 'Sí',
        'data-off': 'No',
    }))
    importe_liq = forms.DecimalField(required=False, label='Importe liquidado', widget=forms.NumberInput({
        'class': 'form-control form-control-sm',
        'placeholder': '0,00'
    }))
    resuelto = forms.BooleanField(required=False, label="Liquidación realizada", widget=forms.CheckboxInput({
        'class': 'toggle-btn',
        'data-on': 'Finalizada',
        'data-off': 'En progreso',
        'data-onStyle': 'success',
        'data-offStyle': 'warning',
        'data-width': '100'
    }))

    class Meta:
        model = Desconocido
        fields = '__all__'

class ActuacionForm(forms.ModelForm):
    fecha_agenda = forms.DateField(required=False, input_formats=['%d/%m/%Y'], label='Fecha agenda', widget=forms.TextInput(
        {
            'class': 'form-control datepicker',
            'placeholder': 'Ej. 01/01/2018'
        }
    ))
    descripcion = forms.CharField(widget=forms.Textarea({
        'rows': '5',
        'width': '100%',
        'class': 'form-control',
        'placeholder': 'Descripción'
    }))

    class Meta:
        model = actuaciones
        fields = ['fecha_agenda', 'descripcion']

class DesconocidoDatosForm(forms.ModelForm):
    titular_candidato = forms.CharField(required=False, label="Titular candidato", widget=forms.TextInput({
        'class': 'form-control form-control-sm',
        'placeholder': 'Nombre y apellidos',
    }))
    nif_candidato = forms.CharField(required=False, label="NIF", widget=forms.TextInput({
        'class': 'form-control form-control-sm',
        'placeholder': 'NIF o CIF'
    }))
    telefono = forms.CharField(required=False, label="Teléfono", widget=forms.TextInput({
        'class': 'form-control form-control-sm',
        'placeholder': 'Número'
    }))
    mt = forms.BooleanField(required=False, label="Modificación de titular realizada", widget=forms.CheckboxInput({
        'class': 'form-check-input pt-3',
        'onchange': "document.getElementById('mtform').disabled = !this.checked;"
    }))
    expediente = forms.CharField(required=False, label="Titular candidato", widget=forms.TextInput({
        'class': 'form-control form-control-sm',
        'placeholder': 'Expediente gtt'
    }))
    liq = forms.BooleanField(required=False, label="Liquidación realizada", widget=forms.CheckboxInput({
        'class': 'form-check-input pt-3'
    }))
    importe_liq = forms.DecimalField(required=False, label='Importe liquidado', widget=forms.NumberInput({
        'class': 'form-control form-control-sm',
        'placeholder': '0,00'
    }))
    class Meta:
        model = Desconocido
        fields = [
            'titular_candidato',
            'nif_candidato',
            'telefono',
            'mt',
            'expediente',
            'liq',
            'importe_liq'
        ]

