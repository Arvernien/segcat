from django.shortcuts import render
from django.template.loader import render_to_string
from .models import Desconocido, actuaciones
from polls.models import organismo
from django.db.models import F, Q, Sum
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views import generic
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import DesconocidoForm, ActuacionForm, DesconocidoDatosForm
from django.shortcuts import get_object_or_404
from datetime import datetime
from django.http import HttpResponseRedirect, JsonResponse
import json

# Create your views here.
@login_required
def Desconocidos(request):
    organismos = organismo.objects.all()
    q = request.GET.get('q')
    if q:
        texto = request.GET.get('q')
        # desc = Desconocido.objects.filter(Q(refcat__icontains=q) |
        #                                   Q(fk_muni__nombre__icontains=q) |
        #                                   Q(fk_muni__org__nombre__icontains=q)
        #                                   ).order_by(((F('b_liquidable') / 100) * F('fk_muni__tipo_impositivo') / 100).desc())
        desc = Desconocido.objects.filter(Q(refcat__icontains=q) |
                                          Q(fk_muni__nombre__icontains=q) |
                                          Q(fk_muni__org__nombre__icontains=q)
                                          ).order_by(
            ((F('b_liquidable') / 100) * F('fk_muni__tipo_impositivo') / 100).desc())
        desc = desc.filter(cuota__gte=F('fk_muni__org__antieconomico'))
    else:
        q = ''
        desc = Desconocido.objects.all().order_by(
            ((F('b_liquidable') / 100) * F('fk_muni__tipo_impositivo') / 100).desc())
        desc = desc.filter(cuota__gte=F('fk_muni__org__antieconomico'))

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
               'organismos': organismos,
               'q': q
               }
    return render(request, 'desconocidos/desconocidos.html', context)

@login_required
def addnota(request):
    form = request.POST
    desconocido = Desconocido.objects.get(pk=form.get('pk'))
    user = User.objects.get(username=request.user)
    getagenda = form.get('fecha_agenda') or None
    if getagenda is not None:
        agenda = datetime.strptime(getagenda, '%d/%m/%Y').strftime('%Y-%m-%d')
    else:
        agenda = None
    desconocido.creaActuacion(user, form.get('descripcion'), datetime.now(), agenda)
    return HttpResponseRedirect(form.get('pk'))

def orgdatos(request):
    form = request.POST
    org = organismo.objects.get(pk=form.get('pk'))
    noresueltos = Desconocido.objects.filter(
        fk_muni__org=org,
        resuelto=False,
        cuota__gte=F('fk_muni__org__antieconomico')
    )
    investigacion = Desconocido.objects.filter(
        fk_muni__org=org,
        resuelto=False,
        tipo__descripcion__icontains='INVESTIG',
        cuota__gte=F('fk_muni__org__antieconomico')
    ).exclude(titular_candidato__isnull=False).count()
    ficticios = Desconocido.objects.filter(
        fk_muni__org=org,
        resuelto=False,
        tipo__descripcion__icontains='FICTICIO',
        cuota__gte=F('fk_muni__org__antieconomico')
    ).exclude(titular_candidato__isnull=False).count()
    resueltos = Desconocido.objects.filter(
        fk_muni__org=org,
        resuelto=True,
        cuota__gte=F('fk_muni__org__antieconomico')
    ).count()
    candidatos = Desconocido.objects.filter(
        fk_muni__org=org,
        resuelto=False,
        cuota__gte=F('fk_muni__org__antieconomico')
    ).exclude(titular_candidato__isnull=True).count()
    mt = Desconocido.objects.filter(
        fk_muni__org=org,
        mt=True,
        cuota__gte=F('fk_muni__org__antieconomico')
    ).count()
    liq = Desconocido.objects.filter(
        fk_muni__org=org,
        liq=True,
        cuota__gte=F('fk_muni__org__antieconomico'))
    sum_liq = liq.aggregate(Sum('importe_liq'))['importe_liq__sum']
    sumaibi = noresueltos.aggregate(Sum('cuota'))['cuota__sum']
    if sum_liq is None:
        sum_liq = 0
    if sumaibi is None:
        sumaibi = 0



    respuesta = {}
    respuesta['investigacion'] = investigacion
    respuesta['ficticios'] = ficticios
    respuesta['resueltos'] = resueltos
    respuesta['candidatos'] = candidatos
    respuesta['mt'] = mt
    respuesta['liq'] = liq.count()
    respuesta['importe_liq'] = sum_liq
    respuesta['pendiente'] = sumaibi

    return JsonResponse(respuesta)

def addnotatest(request):
    form = request.POST
    desconocido = Desconocido.objects.get(pk=form.get('pk'))
    user = User.objects.get(username=request.user)
    getagenda = form.get('fecha_agenda') or None
    print(getagenda)
    if getagenda is not None:
        agenda = datetime.strptime(getagenda, '%d/%m/%Y').strftime('%Y-%m-%d')
    else:
        agenda = None
    desconocido.creaActuacion(user, form.get('descripcion'), datetime.now(), agenda)

    act = actuaciones.objects.filter(desconocido=desconocido).order_by('pk')
    respuesta = {}
    respuesta['data'] = render_to_string('desconocidos/notas.html', {'acts': act})

    return JsonResponse(respuesta)



@login_required
def checknota(request):
    form = request.POST
    actuacion = actuaciones.objects.get(pk=form.get('pk'))
    actuacion.revisado = True
    actuacion.save()
    return HttpResponseRedirect(form.get('descopk'))

def grabadatos(request):
    form = request.POST
    print(form.get('descopk'))
    desco = Desconocido.objects.get(pk=form.get('descopk'))
    desco.titular_candidato = form.get('id_titular_candidato')
    desco.nif_candidato = form.get('id_nif_candidato')
    desco.telefono = form.get('id_telefono')
    #desco.mt = form.get('id_mt')
    desco.expediente = form.get('id_expediente')
    #desco.liq = form.get('id_liq')
    #desco.importe_liq = form.get('id_importe_liq')
    desco.save()
    return HttpResponseRedirect(form.get('descopk'))

@login_required
def detalle(request, pk):
    datos = request.POST or None
    a = get_object_or_404(Desconocido, pk=pk)
    if datos:
        if datos.get('mt') is None:
            a.mt = False
        else:
            a.mt = True
        if datos.get('liq') is None:
            a.liq = False
            a.importe_liq = 0
        else:
            a.liq = True
            if a.importe_liq is None:
                a.importe_liq = 0
            else:
                a.importe_liq = datos.get('importe_liq')
        a.titular_candidato = datos.get('titular_candidato')
        a.nif_candidato = datos.get('nif_candidato')
        a.telefono = datos.get('telefono')
        a.expediente = datos.get('expediente')
        a.save()

    act = actuaciones.objects.filter(desconocido=a).order_by('pk')
    form = DesconocidoForm(instance=a)
    #datosform = DesconocidoDatosForm(request.POST or None, instance=a)
    actform = ActuacionForm()
    refcat = a.refcat
    context = {'desconocido': a,
               'form': form,
               'refcat': refcat,
               'acts': act,
               'formactuacion': actform,
               #'datosform': datosform
     }
    return render(request, 'desconocidos/detalle.html', context)

