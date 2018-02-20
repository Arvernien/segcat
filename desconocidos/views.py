from django.shortcuts import render
from .models import Desconocido
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def Desconocidos(request):
    lista_desc = Desconocido.objects.all()[:100]
    context = {'lista_desc': lista_desc, }
    return render(request, 'desconocidos/desconocidos.html', context)
