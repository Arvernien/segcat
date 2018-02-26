from django import forms
from django.core.exceptions import ValidationError

from .models import Desconocido, actuaciones

class DesconocidoForm(forms.ModelForm):

    class Meta:
        model = Desconocido
        fields = '__all__'

class ActuacionForm(forms.ModelForm):
    fecha_agenda = forms.DateField(required=False, input_formats=['%d/%m/%Y'], label='Fecha agenda', widget=forms.TextInput(
        {
            'class': 'form-control datepicker',
            'placeholder': 'Fecha para agenda'
        }
    ))
    descripcion = forms.CharField(widget=forms.Textarea({
        'rows': '5',
        'width': '100%',
        'class': 'form-control',
        'placeholder': 'Actuación'
    }))

    class Meta:
        model = actuaciones
        fields = ['fecha_agenda', 'descripcion']
