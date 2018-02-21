from django import forms
from django.core.exceptions import ValidationError

from .models import Desconocido

class DesconocidoForm(forms.ModelForm):

    class Meta:
        model = Desconocido
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super(DesconocidoForm).__init__(*args, **kwargs)
