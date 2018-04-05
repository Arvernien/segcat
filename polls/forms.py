from django import forms
from django.core.exceptions import ValidationError
from .models import SubidaFichero



class SubirFichero(forms.ModelForm):
    titulo = forms.CharField(required=False, label="Titulo", widget=forms.TextInput({
        'class': 'form-control',
        'placeholder': 'Descripción del fichero'
    }))
    fichero = forms.FileField(widget=forms.FileInput({
        'class': 'cssfileinput',
        'data-multiple-caption': "{count} files selected"
    }))
    class Meta:
        model = SubidaFichero
        fields = ('titulo', 'fichero')
        exclude = ('usuario', 'nombre')