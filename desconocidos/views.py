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
    investigacion = 0
    ficticios = 0
    resueltos = 0
    candidatos = 0
    mt = 0
    cuentaliq = 0
    sum_liq = 0
    sumaibi = 0
    busqhref = ''
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
            busqhref = 'busqstats/?modo=s&q=' + q
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
            desc = desc.filter(cuota__gte=F('fk_muni__org__antieconomico'))
            busqhref = 'busqstats/?modo=a' \
                       + '&inputOrganismo=' + request.GET.get('inputOrganismo') \
                       + '&inputMunicipio=' + request.GET.get('inputMunicipio') \
                       + '&inputSP=' + request.GET.get('inputSP') \
                       + '&inputCandidato=' + request.GET.get('inputCandidato') \
                       + '&inputTipoFinca=' + request.GET.get('inputTipoFinca') \
                       + '&inputTipo=' + request.GET.get('inputTipo') \
                       + '&inputIbiMin=' + request.GET.get('inputIbiMin') \
                       + '&inputIbiMax=' + request.GET.get('inputIbiMax') \
                       + '&inputMt=' + request.GET.get('inputMt') \
                       + '&inputLiq=' + request.GET.get('inputLiq')
            print(desc.count())
        noresueltos = desc.filter(
            resuelto=False,
            cuota__gte=F('fk_muni__org__antieconomico')
        )

        investigacion = desc.filter(
            resuelto=False,
            tipo__descripcion__icontains='INVESTIG',
            cuota__gte=F('fk_muni__org__antieconomico')
        ).exclude(titular_candidato__isnull=False).count()
        ficticios = desc.filter(
            resuelto=False,
            tipo__descripcion__icontains='FICTICIO',
            cuota__gte=F('fk_muni__org__antieconomico')
        ).exclude(titular_candidato__isnull=False).count()
        resueltos = desc.filter(
            resuelto=True,
            cuota__gte=F('fk_muni__org__antieconomico')
        ).count()
        print(desc.count())
        candidatos = desc.filter(
            resuelto=False,
            cuota__gte=F('fk_muni__org__antieconomico')
        ).exclude(titular_candidato__isnull=True).count()
        mt = desc.filter(
            mt=True,
            cuota__gte=F('fk_muni__org__antieconomico')
        ).count()
        liq = desc.filter(
            liq=True,
            cuota__gte=F('fk_muni__org__antieconomico'))
        cuentaliq = liq.count()
        sum_liq = liq.aggregate(Sum('importe_liq'))['importe_liq__sum']
        sumaibi = noresueltos.aggregate(Sum('cuota'))['cuota__sum']
        if sum_liq is None:
            sum_liq = 0
        if sumaibi is None:
            sumaibi = 0


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
               'modo': request.GET.get('modo'),
               'investigacion': investigacion,
               'ficticios': ficticios,
               'resueltos': resueltos,
               'candidatos': candidatos,
               'mt': mt,
               'liq': cuentaliq,
               'importe_liq': sum_liq,
               'pendiente': sumaibi,
               'busqhref': busqhref
               }
    return render(request, 'desconocidos/desconocidos.html', context)


def pruebas(request):
    investigacion = 0
    ficticios = 0
    resueltos = 0
    candidatos = 0
    mt = 0
    cuentaliq = 0
    sum_liq = 0
    sumaibi = 0
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
            desc = desc.filter(cuota__gte=F('fk_muni__org__antieconomico'))
            print(desc.count())
        noresueltos = desc.filter(
            resuelto=False,
            cuota__gte=F('fk_muni__org__antieconomico')
        )

        investigacion = desc.filter(
            resuelto=False,
            tipo__descripcion__icontains='INVESTIG',
            cuota__gte=F('fk_muni__org__antieconomico')
        ).exclude(titular_candidato__isnull=False).count()
        ficticios = desc.filter(
            resuelto=False,
            tipo__descripcion__icontains='FICTICIO',
            cuota__gte=F('fk_muni__org__antieconomico')
        ).exclude(titular_candidato__isnull=False).count()
        resueltos = desc.filter(
            resuelto=True,
            cuota__gte=F('fk_muni__org__antieconomico')
        ).count()
        print(desc.count())
        candidatos = desc.filter(
            resuelto=False,
            cuota__gte=F('fk_muni__org__antieconomico')
        ).exclude(titular_candidato__isnull=True).count()
        mt = desc.filter(
            mt=True,
            cuota__gte=F('fk_muni__org__antieconomico')
        ).count()
        liq = desc.filter(
            liq=True,
            cuota__gte=F('fk_muni__org__antieconomico'))
        cuentaliq = liq.count()
        sum_liq = liq.aggregate(Sum('importe_liq'))['importe_liq__sum']
        sumaibi = noresueltos.aggregate(Sum('cuota'))['cuota__sum']
        if sum_liq is None:
            sum_liq = 0
        if sumaibi is None:
            sumaibi = 0


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
               'modo': request.GET.get('modo'),
               'investigacion': investigacion,
               'ficticios': ficticios,
               'resueltos': resueltos,
               'candidatos': candidatos,
               'mt': mt,
               'liq': cuentaliq,
               'importe_liq': sum_liq,
               'pendiente': sumaibi,
               }
    return render(request, 'desconocidos/desconocidos_pruebas.html', context)




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
    # a = TramiteForm(request.POST)
    # if a.is_valid():
    #     print(a.cleaned_data['tramite_agenda'])
    desconocido = Desconocido.objects.get(pk=form.get('pk'))
    user = User.objects.get(username=request.user)
    getagenda = form.get('fecha_agenda') or None
    if getagenda is not None:
        agenda = datetime.strptime(getagenda, '%d/%m/%Y').strftime('%Y-%m-%d')
    else:
        agenda = None
    desconocido.creaTramite(user, form.get('ampliacion'), datetime.now(), form.get('tipo'), agenda)
    listatramites = tramites.objects.filter(desconocido=desconocido).order_by('pk')
    respuesta = {}
    respuesta['data'] = render_to_string('desconocidos/actuaciones.html', {'listatramites': listatramites, 'request': request})

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

    act = actuaciones.objects.filter(desconocido=desconocido).order_by('pk')
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
    act = actuaciones.objects.filter(desconocido=desconocido).order_by('pk')
    respuesta = {}
    respuesta['data'] = render_to_string('desconocidos/notas.html', {'acts': act, 'request': request})

    return JsonResponse(respuesta)

@login_required
def checktramite(request):
    form = request.POST
    desconocido = Desconocido.objects.get(pk=form.get('desconocido'))
    tram = tramites.objects.get(pk=form.get('pk'))
    tram.revisado = True
    tram.save()
    tram = tramites.objects.filter(desconocido=desconocido).order_by('pk')
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

@login_required
def orgstats(request, pk):
    org = organismo.objects.get(pk=pk)
    desc = Desconocido.objects.filter(fk_muni__org=org)
    antieconomicos = desc.filter(
        cuota__lt=F('fk_muni__org__antieconomico')
    )

    rusticas = desc.filter(
        tipo_finca__descripcion='RÚSTICA',
        v_constru=0,
        cuota__gte=F('fk_muni__org__antieconomico')
    )
    solares = desc.filter(
        tipo_finca__descripcion='URBANA',
        v_constru=0,
        cuota__gte=F('fk_muni__org__antieconomico')
    )
    investigables = desc.filter(
        v_constru__gt=0,
        cuota__gte=F('fk_muni__org__antieconomico')
    )
    descrustica = desc.filter(tipo_finca__descripcion='RÚSTICA')
    descurbana = desc.filter(tipo_finca__descripcion='URBANA')
    desconocidoscuota = desc.aggregate(Sum('cuota'))['cuota__sum']

    context = {
        'organismo': org,
        'pk': pk,
        'desconocidos': desc,
        'desconocidoscuota': desconocidoscuota,
        'antieconomicos': antieconomicos.count(),
        'antipercent': round((antieconomicos.count()/desc.count())*100, 2),
        'anticuota': antieconomicos.aggregate(Sum('cuota'))['cuota__sum'],
        'antipercentibi': round((antieconomicos.aggregate(Sum('cuota'))['cuota__sum']/desconocidoscuota)*100, 2),
        'rusticas': rusticas.count(),
        'rusticaspercent': round((rusticas.count()/desc.count())*100, 2),
        'rusticascuota': rusticas.aggregate(Sum('cuota'))['cuota__sum'],
        'rusticaspercentibi': round((rusticas.aggregate(Sum('cuota'))['cuota__sum']/desconocidoscuota)*100, 2),
        'solares': solares.count(),
        'solarespercent': round((solares.count()/desc.count())*100, 2),
        'solarescuota': solares.aggregate(Sum('cuota'))['cuota__sum'],
        'solarespercentibi': round((solares.aggregate(Sum('cuota'))['cuota__sum']/desconocidoscuota)*100, 2),
        'investigables': investigables.count(),
        'investigablespercent': round((investigables.count()/desc.count())*100, 2),
        'investigablescuota': investigables.aggregate(Sum('cuota'))['cuota__sum'],
        'investigablespercentibi': round((investigables.aggregate(Sum('cuota'))['cuota__sum']/desconocidoscuota)*100, 2),
        'descrustica': descrustica.count(),
        'descrusticapercent': round((descrustica.count()/desc.count())*100),
        'descrusticacuota': descrustica.aggregate(Sum('cuota'))['cuota__sum'],
        'descrusticapercentibi': round((descrustica.aggregate(Sum('cuota'))['cuota__sum']/desconocidoscuota)*100, 2),
        'descurbana': descurbana.count(),
        'descurbanapercent': round((descurbana.count() / desc.count()) * 100),
        'descurbanacuota': descurbana.aggregate(Sum('cuota'))['cuota__sum'],
        'descurbanapercentibi': round((descurbana.aggregate(Sum('cuota'))['cuota__sum']/desconocidoscuota)*100, 2)
    }

    return render(request, 'desconocidos/organismo.html', context)


@login_required
def busqstats(request):
    modo = request.GET.get('modo')
    q = request.GET.get('q') or ''
    desc = Desconocido.objects.all()
    if modo:
        # ---------------------- Búsqueda simple, utiliza el criterio en "q" para buscar en la referencia catastral
        # ---------------------- nombre de municipio y nombre de organismo.
        if modo == 's':
            desc = Desconocido.objects.filter(Q(refcat__icontains=q) |
                                              Q(fk_muni__nombre__icontains=q) |
                                              Q(fk_muni__org__nombre__icontains=q)
                                              ).order_by(
                ((F('b_liquidable') / 100) * F('fk_muni__tipo_impositivo') / 100).desc())
            #desc = desc.filter(cuota__gte=F('fk_muni__org__antieconomico'))
            busqhref = '/busqstats/?modo=s&q=' + q
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
            desc = desc.filter(cuota__gte=F('fk_muni__org__antieconomico'))
            print(desc.count())

    antiecon = desc.filter(
        cuota__lt=F('fk_muni__org__antieconomico')
    )

    rusticas = desc.filter(
        tipo_finca__descripcion='RÚSTICA',
        v_constru=0,
        cuota__gte=F('fk_muni__org__antieconomico')
    )
    solares = desc.filter(
        tipo_finca__descripcion='URBANA',
        v_constru=0,
        cuota__gte=F('fk_muni__org__antieconomico')
    )
    investigables = desc.filter(
        v_constru__gt=0,
        cuota__gte=F('fk_muni__org__antieconomico')
    )
    descrustica = desc.filter(tipo_finca__descripcion='RÚSTICA')
    descurbana = desc.filter(tipo_finca__descripcion='URBANA')
    desconocidoscuota = desc.aggregate(Sum('cuota'))['cuota__sum']
    if antiecon.count() == 0:
        antieconomicos = 0
    else:
        antieconomicos = antiecon.count()
    if rusticas.count() == 0:
        rusticas = 0
    else:
        rusticas = rusticas.count()
    antipercent = round((antieconomicos / desc.count()) * 100, 2)
    anticuota = antiecon.aggregate(Sum('cuota'))['cuota__sum'] or 0
    antipercentibi = round((anticuota / desconocidoscuota) * 100, 2)
    rusticaspercent = round((rusticas / desc.count()) * 100, 2)
    rusticascuota = rusticas.aggregate(Sum('cuota'))['cuota__sum'] or 0
    rusticaspercentibi = round((rusticascuota / desconocidoscuota) * 100, 2)
    solares = solares.count()
    solarespercent = round((solares.count() / desc.count()) * 100, 2)
    solarescuota = solares.aggregate(Sum('cuota'))['cuota__sum'] or 0
    solarespercentibi = round((solarescuota / desconocidoscuota) * 100, 2)
    investigables = investigables.count()
    investigablespercent = round((investigables.count() / desc.count()) * 100, 2)
    investigablescuota = investigables.aggregate(Sum('cuota'))['cuota__sum'] or 0
    investigablespercentibi = round((investigablescuota / desconocidoscuota) * 100, 2)
    descrustica = descrustica.count(),
    descrusticapercent = round((descrustica.count() / desc.count()) * 100)
    descrusticacuota = descrustica.aggregate(Sum('cuota'))['cuota__sum'] or 0
    descrusticapercentibi = round((descrusticacuota / desconocidoscuota) * 100, 2)
    descurbana = descurbana.count()
    descurbanapercent = round((descurbana.count() / desc.count()) * 100)
    descurbanacuota = descurbana.aggregate(Sum('cuota'))['cuota__sum'] or 0
    descurbanapercentibi = round((descurbanacuota / desconocidoscuota) * 100, 2)

    context = {
        'desconocidos': desc,
        'desconocidoscuota': desconocidoscuota,
        'antieconomicos': antieconomicos.count(),
        'antipercent': antipercent,
        'anticuota': anticuota,
        'antipercentibi': antipercentibi,
        'rusticas': rusticas,
        'rusticaspercent': rusticaspercent,
        'rusticascuota': rusticascuota,
        'rusticaspercentibi': rusticaspercentibi,
        'solares': solares.count(),
        'solarespercent': solarespercent,
        'solarescuota': solarescuota,
        'solarespercentibi': solarespercentibi,
        'investigables': investigables.count(),
        'investigablespercent': investigablespercent,
        'investigablescuota': investigablescuota,
        'investigablespercentibi': investigablespercentibi,
        'descrustica': descrustica,
        'descrusticapercent': descrusticapercent,
        'descrusticacuota': descrusticacuota,
        'descrusticapercentibi': descrusticapercentibi,
        'descurbana': descurbana,
        'descurbanapercent': descurbanapercent,
        'descurbanacuota': descurbanacuota,
        'descurbanapercentibi': descurbanapercentibi
    }

    return render(request, 'desconocidos/organismo.html', context)
