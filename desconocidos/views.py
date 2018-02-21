from django.shortcuts import render
from .models import Desconocido
from django.db.models import F, Q
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import DesconocidoForm

# Create your views here.
@login_required
def Desconocidos(request):
    q = request.GET.get('q')
    if q:
        texto = request.GET.get('q')
        desc = Desconocido.objects.filter(Q(refcat__icontains=q) |
                                          Q(fk_muni__nombre__icontains=q) |
                                          Q(fk_muni__org__nombre__icontains=q)
                                          ).order_by(((F('b_liquidable') / 100) * F('fk_muni__tipo_impositivo') / 100).desc())
    else:
        q = ''
        desc = Desconocido.objects.all().order_by(
            ((F('b_liquidable') / 100) * F('fk_muni__tipo_impositivo') / 100).desc())
    limite_pagina = 50
    paginador = Paginator(desc, limite_pagina)
    pag = request.GET.get('pag')
    lista_desc = paginador.get_page(pag)
    num_paginas = lista_desc.paginator.num_pages
    if not pag:
        pag = 1
    pagina_actual = int(pag)
    total = len(desc)
    inicio = pagina_actual * limite_pagina + 1 - 50
    final = pagina_actual * limite_pagina
    if final > total:
        final = total

    if num_paginas <= 11 or pagina_actual <= 6:
        paginas = [x for x in range(1, min(num_paginas + 1, 12))]
    elif pagina_actual > num_paginas - 6:
        paginas = [x for x in range(num_paginas - 10, num_paginas + 1)]
    else:
        paginas = [x for x in range(pagina_actual - 5, pagina_actual + 6)]
    context = {'lista_desc': lista_desc,
               'paginas': paginas,
               'inicio': inicio,
               'final': final,
               'total': total,
               'q': q
               }
    return render(request, 'desconocidos/desconocidos.html', context)

def detalle(request, pk):
    a = Desconocido.objects.get(pk=pk)
    form = DesconocidoForm()
    context = {'desconocido': a, 'form': form}
    return render(request, 'desconocidos/detalle.html', context)
