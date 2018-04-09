from polls.file_handler import AccessDesconocidos, IdentificaFichero
from django.shortcuts import render
from django.template.loader import render_to_string
from .models import Desconocido, actuaciones, tramites, tipoDesc
from polls.models import organismo, SubidaFichero
from django.db.models import F, Q, Sum
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import DesconocidoForm, ActuacionForm, TramiteForm
from polls.forms import SubirFichero
from django.shortcuts import get_object_or_404
from datetime import datetime
from django.http import HttpResponseRedirect, JsonResponse
from io import BytesIO
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.urls import reverse
from django.conf import settings
import uuid


# Create your views here.


# VISTA PRINCIPAL DE LOS DESCONOCIDOS, SE RENDERIZA A TRAVÉS DE LA PLANTILLA DESCONOCIDOS.HTML
@login_required
def Desconocidos(request):
    investigacion = 0
    ficticios = 0
    resueltos = 0
    candidatos = 0
    investigables = 0
    rusticas = 0
    solares = 0
    antieconomicos = 0
    mt = 0
    cuentaliq = 0
    sum_liq = 0
    sumaibi = 0
    busqhref = ''
    tipos = tipoDesc.objects.all()
    organismos = organismo.objects.all()
    tipo_antiecon = tipoDesc.objects.get(descripcion='ANTIECONÓMICO')
    tipo_investigable = tipoDesc.objects.get(descripcion='INVESTIGABLE')
    tipo_rustica = tipoDesc.objects.get(descripcion='RÚSTICA SOLAR')
    tipo_solar = tipoDesc.objects.get(descripcion='URBANA SOLAR')
    # ------------------- Identifica el tipo de búsqueda s=simple, a=avanzada, si no existe modo muestra todos los
    # desconocidos ------------------------
    modo = request.GET.get('modo')
    q = request.GET.get('q') or ''
    if modo:
        # ------Búsqueda simple, utiliza el criterio en "q" para buscar en la referencia catastral
        # nombre de municipio y nombre de organismo ---------------------- .
        if modo == 's':

            # REALIZA LA BÚSQUEDA FILTRANDO EN LOS CAMPOS DE REFERENCIA CATASTRAL, NOMBRE DEL MUNICIPIO AL QUE
            # PERTENECE EL DESCONOCIDO Y NOMBRE DEL ORGANISMO AL QUE PERTENECE EL MUNICIPIO.

            desc = Desconocido.objects.filter(Q(refcat__icontains=q) |
                                              Q(fk_muni__nombre__icontains=q) |
                                              Q(fk_muni__org__nombre__icontains=q)
                                              ).order_by('-cuota')

            # GENERA LA CADENA DE BÚSQUEDA PARA AÑADIRLA AL ENLACE DEL BOTON EN EL GRÁFICO DE BÚSQUEDA
            busqhref = 'busqstats/?modo=s&q=' + q

        # ---------------------- Búsqueda avanzada, usa los parámetros proporcionados en el formulario para aplicar filtros recursivamente

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
                desc = desc.filter(tipo__id=request.GET.get('inputTipo'))
            if request.GET.get('inputIbiMin') != '':
                desc = desc.filter(cuota__gte=request.GET.get('inputIbiMin'))
            if request.GET.get('inputIbiMax') != '':
                desc = desc.filter(cuota__lte=request.GET.get('inputIbiMax'))
            if request.GET.get('inputMt') != '':
                desc = desc.filter(mt=request.GET.get('inputMt'))
            if request.GET.get('inputLiq') != '':
                desc = desc.filter(liq=request.GET.get('inputLiq'))
            if request.GET.get('inputAntiecon') == 'False':
                desc = desc.filter(cuota__gte=F('fk_muni__org__antieconomico'))


            # GENERA LA CADENA DE BÚSQUEDA PARA AÑADIRLA AL ENLACE DEL BOTON EN EL GRÁFICO DE BÚSQUEDA

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
                       + '&inputLiq=' + request.GET.get('inputLiq') \
                       + '&inputAntiecon=' + request.GET.get('inputAntiecon')

        # APLICA FILTROS PARA SACAR LAS ESTADÍSTICAS NECESARIAS PARA EL GRÁFICO DE LA BÚSQUEDA

        # NO RESUELTOS: AQUELLOS DESCONOCIDOS CON CAMPO BOOLEANO RESUELTO=FALSE
        # noresueltos = desc.filter(
        #     resuelto=False,
        #     #cuota__gte=F('fk_muni__org__antieconomico')
        # )

        antieconomicos = desc.filter(
            tipo=tipo_antiecon
        ).count()

        # CLASIFICADOS COMO EN INVESTIGACION: DESCONOCIDOS CUYO TIPO CONTENGA 'INVESTIG', SEAN NO RESUELTOS Y EL CAMPO
        # TITULAR CANDIDATO ESTÉ VACÍO.

        rusticas = desc.filter(
            tipo=tipo_rustica
        ).count()

        # investigacion = desc.filter(
        #     resuelto=False,
        #     tipo__descripcion__icontains='INVESTIG',
        #     #cuota__gte=F('fk_muni__org__antieconomico')
        # ).exclude(titular_candidato__isnull=False).count()

        # CLASIFICADOS COMO EN INVESTIGACION: DESCONOCIDOS CUYO TIPO CONTENGA 'FICTICIO', SEAN NO RESUELTOS Y EL CAMPO
        # TITULAR CANDIDATO ESTÉ VACÍO.
        solares = desc.filter(
            tipo=tipo_solar
        ).count()

        # ficticios = desc.filter(
        #     resuelto=False,
        #     tipo__descripcion__icontains='FICTICIO',
        #     #cuota__gte=F('fk_muni__org__antieconomico')
        # ).exclude(titular_candidato__isnull=False).count()

        # RESUELTOS: AQUELLOS DESCONOCIDOS CON CAMPO BOOLEANO RESUELTO=TRUE
        investigables = desc.filter(
            tipo=tipo_investigable
        ).count()
        # resueltos = desc.filter(
        #     resuelto=True,
        #     #cuota__gte=F('fk_muni__org__antieconomico')
        # ).count()

        # CANDIDATOS: AQUELLOS DESCONOCIDOS NO RESUELTOS Y CUYO CAMPO TITULAR_CANDIDATO NO ESTÉ EN BLANCO
        # candidatos = desc.filter(
        #     resuelto=False,
        #     #cuota__gte=F('fk_muni__org__antieconomico')
        # ).exclude(titular_candidato__isnull=True).count()

        # MODIFICACIONES DE TITULAR: DESCONOCIDOS CON EL CAMPO BOOLEANO MT=TRUE
        mt = desc.filter(
            mt=True,
            #cuota__gte=F('fk_muni__org__antieconomico')
        ).count()

        # LIQUIDADOS: DESCONOCIDOS CON EL CAMPO BOOLEANO LIQ=TRUE
        liq = desc.filter(
            liq=True,
            #cuota__gte=F('fk_muni__org__antieconomico')
            )
        cuentaliq = liq.count()

        # SUMA DE LAS LIQUIDACIONES REALIZADAS Y DE LA CUOTA DE IBI DE LOS NO RESUELTOS
        sum_liq = liq.aggregate(Sum('importe_liq'))['importe_liq__sum']
        sumaibi = desc.aggregate(Sum('cuota'))['cuota__sum']
        if sum_liq is None:
            sum_liq = 0
        if sumaibi is None:
            sumaibi = 0

    # SI NO EXISTE MODO, DEVUELVE TODOS LOS DESCONOCIDOS ORDENADOS POR CUOTA DESCENDENTE
    else:
        desc = Desconocido.objects.all().order_by('-cuota')
        #desc = desc.filter(cuota__gte=F('fk_muni__org__antieconomico'))

    # PAGINADOR
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
               # 'investigacion': investigacion,
               # 'ficticios': ficticios,
               # 'resueltos': resueltos,
               # 'candidatos': candidatos,
               'investigables': investigables,
               'rusticas': rusticas,
               'solares': solares,
               'antieconomicos': antieconomicos,
               'mt': mt,
               'liq': cuentaliq,
               'importe_liq': sum_liq,
               'pendiente': sumaibi,
               'busqhref': busqhref,
               'total': desc.count(),
               'tipos': tipos
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
    tipo_antiecon = tipoDesc.objects.get(descripcion='ANTIECONÓMICO')
    tipo_investigable = tipoDesc.objects.get(descripcion='INVESTIGABLE')
    tipo_rustica = tipoDesc.objects.get(descripcion='RÚSTICA SOLAR')
    tipo_solar = tipoDesc.objects.get(descripcion='URBANA SOLAR')
    # noresueltos = Desconocido.objects.filter(
    #     fk_muni__org=org,
    #     resuelto=False,
    #     #cuota__gte=F('fk_muni__org__antieconomico')
    # )
    # investigacion = Desconocido.objects.filter(
    #     fk_muni__org=org,
    #     resuelto=False,
    #     tipo__descripcion__icontains='INVESTIG',
    #     #cuota__gte=F('fk_muni__org__antieconomico')
    # ).exclude(titular_candidato__isnull=False).count()
    # ficticios = Desconocido.objects.filter(
    #     fk_muni__org=org,
    #     resuelto=False,
    #     tipo__descripcion__icontains='FICTICIO',
    #     #cuota__gte=F('fk_muni__org__antieconomico')
    # ).exclude(titular_candidato__isnull=False).count()
    # resueltos = Desconocido.objects.filter(
    #     fk_muni__org=org,
    #     resuelto=True,
    #     #cuota__gte=F('fk_muni__org__antieconomico')
    # ).count()
    # candidatos = Desconocido.objects.filter(
    #     fk_muni__org=org,
    #     resuelto=False,
    #     #cuota__gte=F('fk_muni__org__antieconomico')
    # ).exclude(titular_candidato__isnull=True).count()
    investigables = Desconocido.objects.filter(
        fk_muni__org=org,
        tipo=tipo_investigable
    ).count()
    rusticas = Desconocido.objects.filter(
        fk_muni__org=org,
        tipo=tipo_rustica
    ).count()
    solares = Desconocido.objects.filter(
        fk_muni__org=org,
        tipo=tipo_solar
    ).count()
    antieconomicos = Desconocido.objects.filter(
        fk_muni__org=org,
        tipo=tipo_antiecon
    ).count()
    mt = Desconocido.objects.filter(
        fk_muni__org=org,
        mt=True,
        #cuota__gte=F('fk_muni__org__antieconomico')
    ).count()
    liq = Desconocido.objects.filter(
        fk_muni__org=org,
        liq=True,
        #cuota__gte=F('fk_muni__org__antieconomico')
        )
    sum_liq = liq.aggregate(Sum('importe_liq'))['importe_liq__sum']
    sumaibi = Desconocido.objects.filter(fk_muni__org=org).aggregate(Sum('cuota'))['cuota__sum']
    if sum_liq is None:
        sum_liq = 0
    if sumaibi is None:
        sumaibi = 0
    total = Desconocido.objects.filter(fk_muni__org=org).count()


    respuesta = {}
    respuesta['antieconomicos'] = antieconomicos
    respuesta['rusticas'] = rusticas
    respuesta['investigables'] = investigables
    respuesta['solares'] = solares
    respuesta['mt'] = mt
    respuesta['liq'] = liq.count()
    respuesta['importe_liq'] = sum_liq
    respuesta['pendiente'] = sumaibi
    respuesta['total'] = total

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

    # Cálculo de estadísticas

    desconocidoscuota = desc.aggregate(Sum('cuota'))['cuota__sum']
    organismocuota = \
        organismo.objects.filter(id__in=desc.values('fk_muni__org').distinct()).aggregate(Sum('padron_ibi'))[
            'padron_ibi__sum']
    organismoOT = \
        organismo.objects.filter(id__in=desc.values('fk_muni__org').distinct()).aggregate(Sum('padron_n_OT'))[
            'padron_n_OT__sum']
    print('organismoOT:', organismoOT)
    if desconocidoscuota is None:
        desconocidoscuota = 0

    # ANTIECONÓMICOS
    if antieconomicos.count() == 0:
        antieconomicos = 0
        anticuota = 0
        antipercent = 0
        antipercentibi = 0
        antipercentibitotal = 0
        antipercentOT = 0
    else:
        anticuota = antieconomicos.aggregate(Sum('cuota'))['cuota__sum'] or 0
        antipercentibitotal = round((anticuota / organismocuota)*100, 2)
        antieconomicos = antieconomicos.count()
        antipercent = round((antieconomicos / desc.count()) * 100, 2)
        antipercentibi = round((anticuota / desconocidoscuota) * 100, 2)
        antipercentOT = round((antieconomicos/organismoOT)*100, 2)


    # RÚSTICAS SIN CONSTRUCCIÓN
    if rusticas.count() == 0:
        rusticas = 0
        rusticaspercent = 0
        rusticascuota = 0
        rusticaspercentibi = 0
        rusticaspercentibitotal = 0
        rusticaspercentOT = 0
    else:
        rusticascuota = rusticas.aggregate(Sum('cuota'))['cuota__sum'] or 0
        rusticaspercentibitotal = round((rusticascuota / organismocuota) * 100, 2)
        rusticas = rusticas.count()
        rusticaspercent = round((rusticas / desc.count()) * 100, 2)
        rusticaspercentibi = round((rusticascuota / desconocidoscuota) * 100, 2)
        rusticaspercentOT = round((rusticas/organismoOT)*100, 2)


    # SOLARES
    if solares.count() == 0:
        solares = 0
        solarespercent = 0
        solarescuota = 0
        solarespercentibi = 0
        solarespercentibitotal = 0
        solarespercentOT = 0
    else:
        solarescuota = solares.aggregate(Sum('cuota'))['cuota__sum'] or 0
        solarespercentibitotal = round((solarescuota / organismocuota) * 100, 2)
        solares = solares.count()
        solarespercent = round((solares / desc.count()) * 100, 2)
        solarespercentibi = round((solarescuota / desconocidoscuota) * 100, 2)
        solarespercentOT = round((solares / organismoOT) * 100, 2)

    # INVESTIGABLES
    if investigables.count() == 0:
        investigables = 0
        investigablespercent = 0
        investigablescuota = 0
        investigablespercentibi = 0
        investigablespercentibitotal = 0
        investigablespercentOT = 0
    else:
        investigablescuota = investigables.aggregate(Sum('cuota'))['cuota__sum'] or 0
        investigablespercentibitotal = round((investigablescuota / organismocuota) * 100, 2)
        investigables = investigables.count()
        investigablespercent = round((investigables / desc.count()) * 100, 2)
        investigablespercentibi = round((investigablescuota / desconocidoscuota) * 100, 2)
        investigablespercentOT = round((investigables/organismoOT)*100, 2)

    # CLASIFICACIÓN RÚSTICA
    if descrustica.count() == 0:
        descrustica = 0
        descrusticapercent = 0
        descrusticacuota = 0
        descrusticapercentibi = 0
        descrusticapercentibitotal = 0
        descrusticapercentOT = 0
    else:
        descrusticacuota = descrustica.aggregate(Sum('cuota'))['cuota__sum'] or 0
        descrusticapercentibitotal = round((descrusticacuota / organismocuota) * 100, 2)
        descrustica = descrustica.count()
        descrusticapercent = round((descrustica / desc.count()) * 100)
        descrusticapercentibi = round((descrusticacuota / desconocidoscuota) * 100, 2)
        descrusticapercentOT = round((descrustica/organismoOT)*100, 2)

    # CLASIFICACIÓN URBANA
    if descurbana.count() == 0:
        descurbana = 0
        descurbanapercent = 0
        descurbanacuota = 0
        descurbanapercentibi = 0
        descurbanapercentibitotal = 0
        descurbanapercentOT = 0
    else:
        descurbanacuota = descurbana.aggregate(Sum('cuota'))['cuota__sum'] or 0
        descurbanapercentibitotal = round((descurbanacuota / organismocuota) * 100, 2)
        descurbana = descurbana.count()
        descurbanapercent = round((descurbana / desc.count()) * 100)
        descurbanapercentibi = round((descurbanacuota / desconocidoscuota) * 100, 2)
        descurbanapercentOT = round((descurbana/organismoOT)*100, 2)

    ibipercenttotal = round((desconocidoscuota/organismocuota)*100, 2)
    percenttotalOT = round((desc.count()/organismoOT)*100, 2)


    context = {
        'titulo': org.nombre,
        'desconocidos': desc,
        'desconocidoscuota': desconocidoscuota,
        'antieconomicos': antieconomicos,
        'antipercent': antipercent,
        'anticuota': anticuota,
        'antipercentibi': antipercentibi,
        'antipercentibitotal': antipercentibitotal,
        'antipercentOT': antipercentOT,
        'rusticas': rusticas,
        'rusticaspercent': rusticaspercent,
        'rusticascuota': rusticascuota,
        'rusticaspercentibi': rusticaspercentibi,
        'rusticaspercentibitotal': rusticaspercentibitotal,
        'rusticaspercentOT': rusticaspercentOT,
        'solares': solares,
        'solarespercent': solarespercent,
        'solarescuota': solarescuota,
        'solarespercentibi': solarespercentibi,
        'solarespercentibitotal': solarespercentibitotal,
        'solarespercentOT': solarespercentOT,
        'investigables': investigables,
        'investigablespercent': investigablespercent,
        'investigablescuota': investigablescuota,
        'investigablespercentibi': investigablespercentibi,
        'investigablespercentibitotal': investigablespercentibitotal,
        'investigablespercentOT': investigablespercentOT,
        'descrustica': descrustica,
        'descrusticapercent': descrusticapercent,
        'descrusticacuota': descrusticacuota,
        'descrusticapercentibi': descrusticapercentibi,
        'descrusticapercentibitotal': descrusticapercentibitotal,
        'descrusticapercentOT': descrusticapercentOT,
        'descurbana': descurbana,
        'descurbanapercent': descurbanapercent,
        'descurbanacuota': descurbanacuota,
        'descurbanapercentibi': descurbanapercentibi,
        'descurbanapercentibitotal': descurbanapercentibitotal,
        'descurbanapercentOT': descurbanapercentOT,
        'ibipercenttotal': ibipercenttotal,
        'percenttotalOT': percenttotalOT
    }

    # context = {
    #     'organismo': org,
    #     'pk': pk,
    #     'desconocidos': desc,
    #     'desconocidoscuota': desconocidoscuota,
    #     'antieconomicos': antieconomicos.count(),
    #     'antipercent': round((antieconomicos.count()/desc.count())*100, 2),
    #     'anticuota': antieconomicos.aggregate(Sum('cuota'))['cuota__sum'],
    #     'antipercentibi': round((antieconomicos.aggregate(Sum('cuota'))['cuota__sum']/desconocidoscuota)*100, 2),
    #     'rusticas': rusticas.count(),
    #     'rusticaspercent': round((rusticas.count()/desc.count())*100, 2),
    #     'rusticascuota': rusticas.aggregate(Sum('cuota'))['cuota__sum'],
    #     'rusticaspercentibi': round((rusticas.aggregate(Sum('cuota'))['cuota__sum']/desconocidoscuota)*100, 2),
    #     'solares': solares.count(),
    #     'solarespercent': round((solares.count()/desc.count())*100, 2),
    #     'solarescuota': solares.aggregate(Sum('cuota'))['cuota__sum'],
    #     'solarespercentibi': round((solares.aggregate(Sum('cuota'))['cuota__sum']/desconocidoscuota)*100, 2),
    #     'investigables': investigables.count(),
    #     'investigablespercent': round((investigables.count()/desc.count())*100, 2),
    #     'investigablescuota': investigables.aggregate(Sum('cuota'))['cuota__sum'],
    #     'investigablespercentibi': round((investigables.aggregate(Sum('cuota'))['cuota__sum']/desconocidoscuota)*100, 2),
    #     'descrustica': descrustica.count(),
    #     'descrusticapercent': round((descrustica.count()/desc.count())*100),
    #     'descrusticacuota': descrustica.aggregate(Sum('cuota'))['cuota__sum'],
    #     'descrusticapercentibi': round((descrustica.aggregate(Sum('cuota'))['cuota__sum']/desconocidoscuota)*100, 2),
    #     'descurbana': descurbana.count(),
    #     'descurbanapercent': round((descurbana.count() / desc.count()) * 100),
    #     'descurbanacuota': descurbana.aggregate(Sum('cuota'))['cuota__sum'],
    #     'descurbanapercentibi': round((descurbana.aggregate(Sum('cuota'))['cuota__sum']/desconocidoscuota)*100, 2)
    # }

    return render(request, 'desconocidos/organismo.html', context)


@login_required
def busqstats(request):
    modo = request.GET.get('modo')
    q = request.GET.get('q') or ''
    desc = Desconocido.objects.all()
    # Búsqueda
    if modo:
        # ---------------------- Búsqueda simple, utiliza el criterio en "q" para buscar en la referencia catastral
        # ---------------------- nombre de municipio y nombre de organismo.
        if modo == 's':
            desc = Desconocido.objects.filter(Q(refcat__icontains=q) |
                                              Q(fk_muni__nombre__icontains=q) |
                                              Q(fk_muni__org__nombre__icontains=q)
                                              ).order_by('-cuota')
            #desc = desc.filter(cuota__gte=F('fk_muni__org__antieconomico'))
            busqhref = '/busqstats/?modo=s&q=' + q
            print('busqueda simple')
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
            if request.GET.get('inputAntiecon') == 'False':
                desc = desc.filter(cuota__gte=F('fk_muni__org__antieconomico'))
            print(desc.count())
    # Aplicar filtros para estadísticas
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

    # Cálculo de estadísticas

    desconocidoscuota = desc.aggregate(Sum('cuota'))['cuota__sum']
    organismocuota = \
        organismo.objects.filter(id__in=desc.values('fk_muni__org').distinct()).aggregate(Sum('padron_ibi'))[
            'padron_ibi__sum']
    organismoOT = \
        organismo.objects.filter(id__in=desc.values('fk_muni__org').distinct()).aggregate(Sum('padron_n_OT'))[
            'padron_n_OT__sum']
    print(organismo.objects.filter(id__in=desc.values('fk_muni__org').distinct()))
    if desconocidoscuota is None:
        desconocidoscuota = 0

    # ANTIECONÓMICOS
    if antieconomicos.count() == 0:
        antieconomicos = 0
        anticuota = 0
        antipercent = 0
        antipercentibi = 0
        antipercentibitotal = 0
        antipercentOT = 0
    else:
        anticuota = antieconomicos.aggregate(Sum('cuota'))['cuota__sum'] or 0
        antipercentibitotal = round((anticuota / organismocuota) * 100, 2)
        antieconomicos = antieconomicos.count()
        antipercent = round((antieconomicos / desc.count()) * 100, 2)
        antipercentibi = round((anticuota / desconocidoscuota) * 100, 2)
    antipercentOT = round((antieconomicos / organismoOT) * 100, 2)

    # RÚSTICAS SIN CONSTRUCCIÓN
    if rusticas.count() == 0:
        rusticas = 0
        rusticaspercent = 0
        rusticascuota = 0
        rusticaspercentibi = 0
        rusticaspercentibitotal = 0
        rusticaspercentOT = 0
    else:
        rusticascuota = rusticas.aggregate(Sum('cuota'))['cuota__sum'] or 0
        rusticaspercentibitotal = round((rusticascuota / organismocuota) * 100, 2)
        rusticas = rusticas.count()
        rusticaspercent = round((rusticas / desc.count()) * 100, 2)
        rusticaspercentibi = round((rusticascuota / desconocidoscuota) * 100, 2)
        rusticaspercentOT = round((rusticas / organismoOT) * 100, 2)

    # SOLARES
    if solares.count() == 0:
        solares = 0
        solarespercent = 0
        solarescuota = 0
        solarespercentibi = 0
        solarespercentibitotal = 0
        solarespercentOT = 0
    else:
        solarescuota = solares.aggregate(Sum('cuota'))['cuota__sum'] or 0
        solarespercentibitotal = round((solarescuota / organismocuota) * 100, 2)
        solares = solares.count()
        solarespercent = round((solares / desc.count()) * 100, 2)
        solarespercentibi = round((solarescuota / desconocidoscuota) * 100, 2)
        solarespercentOT = round((solares / organismoOT) * 100, 2)


    # INVESTIGABLES
    if investigables.count() == 0:
        investigables = 0
        investigablespercent = 0
        investigablescuota = 0
        investigablespercentibi = 0
        investigablespercentibitotal = 0
        investigablespercentOT = 0
    else:
        investigablescuota = investigables.aggregate(Sum('cuota'))['cuota__sum'] or 0
        investigablespercentibitotal = round((investigablescuota / organismocuota) * 100, 2)
        investigables = investigables.count()
        investigablespercent = round((investigables / desc.count()) * 100, 2)
        investigablespercentibi = round((investigablescuota / desconocidoscuota) * 100, 2)
        investigablespercentOT = round((investigables / organismoOT) * 100, 2)

    # CLASIFICACIÓN RÚSTICA
    if descrustica.count() == 0:
        descrustica = 0
        descrusticapercent = 0
        descrusticacuota = 0
        descrusticapercentibi = 0
        descrusticapercentibitotal = 0
        descrusticapercentOT = 0
    else:
        descrusticacuota = descrustica.aggregate(Sum('cuota'))['cuota__sum'] or 0
        descrusticapercentibitotal = round((descrusticacuota / organismocuota) * 100, 2)
        descrustica = descrustica.count()
        descrusticapercent = round((descrustica / desc.count()) * 100)
        descrusticapercentibi = round((descrusticacuota / desconocidoscuota) * 100, 2)
        descrusticapercentOT = round((descrustica / organismoOT) * 100, 2)

    # CLASIFICACIÓN URBANA
    if descurbana.count() == 0:
        descurbana = 0
        descurbanapercent = 0
        descurbanacuota = 0
        descurbanapercentibi = 0
        descurbanapercentibitotal = 0
        descurbanapercentOT = 0
    else:
        descurbanacuota = descurbana.aggregate(Sum('cuota'))['cuota__sum'] or 0
        descurbanapercentibitotal = round((descurbanacuota / organismocuota) * 100, 2)
        descurbana = descurbana.count()
        descurbanapercent = round((descurbana / desc.count()) * 100)
        descurbanapercentibi = round((descurbanacuota / desconocidoscuota) * 100, 2)
        descurbanapercentOT = round((descurbana / organismoOT) * 100, 2)

    ibipercenttotal = round((desconocidoscuota / organismocuota) * 100, 2)
    percenttotalOT = round((desc.count() / organismoOT) * 100, 2)

    context = {
        'titulo': 'Resultado de la búsqueda',
        'desconocidos': desc,
        'desconocidoscuota': desconocidoscuota,
        'antieconomicos': antieconomicos,
        'antipercent': antipercent,
        'anticuota': anticuota,
        'antipercentibi': antipercentibi,
        'antipercentibitotal': antipercentibitotal,
        'antipercentOT': antipercentOT,
        'rusticas': rusticas,
        'rusticaspercent': rusticaspercent,
        'rusticascuota': rusticascuota,
        'rusticaspercentibi': rusticaspercentibi,
        'rusticaspercentibitotal': rusticaspercentibitotal,
        'rusticaspercentOT': rusticaspercentOT,
        'solares': solares,
        'solarespercent': solarespercent,
        'solarescuota': solarescuota,
        'solarespercentibi': solarespercentibi,
        'solarespercentibitotal': solarespercentibitotal,
        'solarespercentOT': solarespercentOT,
        'investigables': investigables,
        'investigablespercent': investigablespercent,
        'investigablescuota': investigablescuota,
        'investigablespercentibi': investigablespercentibi,
        'investigablespercentibitotal': investigablespercentibitotal,
        'investigablespercentOT': investigablespercentOT,
        'descrustica': descrustica,
        'descrusticapercent': descrusticapercent,
        'descrusticacuota': descrusticacuota,
        'descrusticapercentibi': descrusticapercentibi,
        'descrusticapercentibitotal': descrusticapercentibitotal,
        'descrusticapercentOT': descrusticapercentOT,
        'descurbana': descurbana,
        'descurbanapercent': descurbanapercent,
        'descurbanacuota': descurbanacuota,
        'descurbanapercentibi': descurbanapercentibi,
        'descurbanapercentibitotal': descurbanapercentibitotal,
        'descurbanapercentOT': descurbanapercentOT,
        'ibipercenttotal': ibipercenttotal,
        'percenttotalOT': percenttotalOT
    }

    return render(request, 'desconocidos/organismo.html', context)

def borrafichero(request, pk):
    fichero = SubidaFichero.objects.get(pk=pk)
    fichero.delete()
    return HttpResponseRedirect(reverse('desconocidos:subir'))

def subefichero(request):
    carga = {}
    ficheros_cargados = None
    respuesta = {}
    print('subida')
    print(request.method)
    if request.method == 'POST':
        form = SubirFichero(request.POST, request.FILES)
        print(form.is_valid())
        if form.is_valid():
            subida = form.save(commit=False)
            subida.nombre = request.FILES['fichero'].name
            subida.usuario = request.user
            subida.save()

            if IdentificaFichero(subida.fichero.path) == 'DESCONOCIDOS':
                carga = AccessDesconocidos(subida.fichero.path)

            # with open(subida.fichero.path, newline='') as archivo:
            #     try:
            #         tipo = archivo.readline().split(';')[0]
            #         if tipo == 'DESCONOCIDOS':
            #             carga = AccessDesconocidos(subida.fichero.path)
            #             carga['tipo'] = 'desconocidos'
            #             print(carga['cargados'])
            #
            #     except:
            #         pass
                respuesta = {
                    'jare': 'jare',
                    'tabla_cargados': carga['tabla_cargados'],
                    'tabla_errores': carga['tabla_errores'],
                    'tabla_finalizados': carga['tabla_finalizados']
                }
            return JsonResponse(respuesta)
        else:
            return render(request, 'desconocidos/upload.html', {'form': form, 'carga':carga, 'ficheros': ficheros_cargados})
    else:
        form = SubirFichero()
        ficheros_cargados = SubidaFichero.objects.all()
        return render(request, 'desconocidos/upload.html', {'form': form, 'carga':carga, 'ficheros': ficheros_cargados})



def pdftest(request):
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="' + str(uuid.uuid4()) + '.pdf"'

    buffer = BytesIO()

    # Create the PDF object, using the BytesIO object as its "file."
    p = canvas.Canvas(buffer)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(100, 100, "Hello world.")
    p.drawImage('D:/Almacen/Web/segcat/polls/static/img/gmaps.png', 10, 10)


    # Close the PDF object cleanly.
    p.showPage()
    p.save()

    # Get the value of the BytesIO buffer and write it to the response.
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response
