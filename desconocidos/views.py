from django.shortcuts import render
from .models import Desconocido
from django.db.models import F
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def Desconocidos(request):
    if request.method == "POST" and request.POST.get('criterio') != '':
        texto = request.POST.get('criterio')
        lista_desc = Desconocido.objects.filter(refcat__icontains=texto).order_by(((F('b_liquidable') / 100) * F('fk_muni__tipo_impositivo') / 100).desc())[:100]
        context = {'lista_desc': lista_desc, }
    else:
        lista_desc = Desconocido.objects.all().order_by(
            ((F('b_liquidable') / 100) * F('fk_muni__tipo_impositivo') / 100).desc())[:100]
        context = {'lista_desc': lista_desc, }
    return render(request, 'desconocidos/desconocidos.html', context)
