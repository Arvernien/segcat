from django.shortcuts import render
from django.template.loader import render_to_string
from .models import Desconocido, actuaciones, tramites
from polls.models import organismo
from django.db.models import F, Q, Sum
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views import generic
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import DesconocidoForm, ActuacionForm, TramiteForm
from django.shortcuts import get_object_or_404
from datetime import datetime
from django.http import HttpResponseRedirect, JsonResponse
import json

# Create your views here.
@login_required
def Desconocidos(request):
    organismos = organismo.objects.all()
    # ------------------- Identifica el tipo de búsqueda s=simple, a=avanzada ------------------------
    modo = request.GET.get('modo')
    q = request.GET.get('q') or ''
    if modo:
        # ---------------------- Búsqueda simple, utiliza el criterio en "q" para buscar en la referencia catastral
        # ---------------------- nombre de municipio y nombre de organismo.
        if modo == 's':

            desc = Desconocido.objects.filter(Q(refcat__icontains=q) |
                                              Q(fk_muni__nombre__icontains=q) |
                                              Q(fk_muni__org__nombre__icontains=q)
                                              ).order_by(
                ((F('b_liquidable') / 100) * F('fk_muni__tipo_impositivo') / 100).desc())
            desc = desc.filter(cuota__gte=F('fk_muni__org__antieconomico'))
        # ---------------------- Búsqueda avanzada, usa los parámetros proporcionados en el formulario para buscar
        elif modo == 'a':
            desc = Desconocido.objects.all().order_by('-cuota')
            if request.GET.get('inputOrganismo') != '':
                desc = desc.filter(fk_muni__org__pk=request.GET.get('inputOrganismo'))
            if request.GET.get('inputMunicipio') != '':
                desc = desc.filter(fk_muni__nombre__icontains=request.GET.get('inputMunicipio'))
            if request.GET.get('inputSP') != '':
                desc = desc.filter(sujeto_pasivo__icontains=request.GET.get('inputSP'))
            if request.GET.get('inputCandidato') != '':
                desc = desc.filter(titular_candidato__icontains=request.GET.get('inputCandidato'))
            if request.GET.get('inputTipoFinca') != '':
                desc = desc.filter(tipo_finca__descripcion__icontains=request.GET.get('inputTipoFinca'))
            if request.GET.get('inputTipo') != '':
                desc = desc.filter(tipo__descripcion__icontains=request.GET.get('inputTipo'))
            if request.GET.get('inputIbiMin') != '':
                desc = desc.filter(cuota__gte=request.GET.get('inputIbiMin'))
            if request.GET.get('inputIbiMax') != '':
                desc = desc.filter(cuota__lte=request.GET.get('inputIbiMax'))
            if request.GET.get('inputMt') != '':
                desc = desc.filter(mt=request.GET.get('inputMt'))
            if request.GET.get('inputLiq') != '':
                desc = desc.filter(liq=request.GET.get('inputLiq'))
            desc.filter(cuota__gte=F('fk_muni__org__antieconomico'))
    else:
        # desc = Desconocido.objects.all().order_by(
        #     ((F('b_liquidable') / 100) * F('fk_muni__tipo_impositivo') / 100).desc())
        desc = Desconocido.objects.all().order_by('-cuota')
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
               'q': q,
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

@login_required
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

@login_required
def addtramite(request):
    form = request.POST
    desconocido = Desconocido.objects.get(pk=form.get('pk'))
    user = User.objects.get(username=request.user)
    getagenda = form.get('fecha_agenda') or None
    print(form.get('tipo'))
    if getagenda is not None:
        agenda = datetime.strptime(getagenda, '%d/%m/%Y').strftime('%Y-%m-%d')
    else:
        agenda = None
    desconocido.creaTramite(user, form.get('ampliacion'), datetime.now(), form.get('tipo'), agenda)

    listatramites = tramites.objects.filter(desconocido=desconocido).order_by('pk')
    respuesta = {}
    respuesta['data'] = render_to_string('desconocidos/actuaciones.html', {'listatramites': listatramites})

    return JsonResponse(respuesta)

@login_required
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

    act = actuaciones.objects.filter(desconocido=desconocido).order_by('-pk')
    respuesta = {}
    respuesta['data'] = render_to_string('desconocidos/notas.html', {'acts': act, 'request': request})

    return JsonResponse(respuesta)



@login_required
def checknota(request):
    form = request.POST
    print(form.get('desconocido'))
    desconocido = Desconocido.objects.get(pk=form.get('desconocido'))
    act = actuaciones.objects.get(pk=form.get('pk'))
    act.revisado = True
    act.save()
    act = actuaciones.objects.filter(desconocido=desconocido).order_by('-pk')
    respuesta = {}
    respuesta['data'] = render_to_string('desconocidos/notas.html', {'acts': act, 'request': request})

    return JsonResponse(respuesta)

@login_required
def checktramite(request):
    form = request.POST
    print(form.get('pk'))
    print(form.get('desconocido'))
    desconocido = Desconocido.objects.get(pk=form.get('desconocido'))
    print(desconocido)
    tram = tramites.objects.get(pk=form.get('pk'))
    tram.revisado = True
    tram.save()
    tram = tramites.objects.filter(desconocido=desconocido)
    print(tram)
    respuesta = {}
    respuesta['data'] = render_to_string('desconocidos/actuaciones.html', {'listatramites': tram, 'request': request})

    return JsonResponse(respuesta)

@login_required
def grabadatos(request):
    form = request.POST
    print(form.get('descopk'))
    desco = Desconocido.objects.get(pk=form.get('descopk'))
    desco.titular_candidato = form.get('id_titular_candidato')
    desco.nif_candidato = form.get('id_nif_candidato')
    desco.telefono = form.get('id_telefono')
    desco.expediente = form.get('id_expediente')
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
        if datos.get('resuelto') is None:
            a.resuelto = False
        else:
            a.resuelto = True
        if datos.get('liq') is None:
            a.liq = False
            a.importe_liq = None
        else:
            a.liq = True
            if datos.get('importe_liq') == '':
                a.importe_liq = None
            else:
                a.importe_liq = datos.get('importe_liq')
        a.titular_candidato = datos.get('titular_candidato')
        a.nif_candidato = datos.get('nif_candidato')
        a.telefono = datos.get('telefono')
        a.expediente = datos.get('expediente')

        a.save()
    listatramites = tramites.objects.filter(desconocido=a).order_by('pk')
    act = actuaciones.objects.filter(desconocido=a).order_by('pk')
    form = DesconocidoForm(instance=a)
    #datosform = DesconocidoDatosForm(request.POST or None, instance=a)
    actform = ActuacionForm()
    tramiteform = TramiteForm()
    refcat = a.refcat
    context = {'desconocido': a,
               'form': form,
               'refcat': refcat,
               'acts': act,
               'formactuacion': actform,
               'tramiteform': tramiteform,
               'listatramites': listatramites,

     }
    return render(request, 'desconocidos/detalle.html', context)

