from django import forms
from django.core.exceptions import ValidationError
from .models import SubidaFichero



class SubirFichero(forms.ModelForm):
    titulo = forms.CharField(required=False, label="Titulo", widget=forms.TextInput({
        'class': 'form-control',
        'placeholder': 'Titulo'
    }))
    fichero = forms.FileField(widget=forms.FileInput({
        'class': 'custom-file-input',
    }))
    class Meta:
        model = SubidaFichero
        fields = ('titulo', 'fichero')
        exclude = ('usuario', 'nombre')