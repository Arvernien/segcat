from django import forms
from django.core.exceptions import ValidationError

from .models import Desconocido

class DesconocidoForm(forms.ModelForm):

    class Meta:
        model = Desconocido
        fields = '__all__'

