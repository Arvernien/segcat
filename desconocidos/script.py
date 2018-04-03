from polls.models import municipio, organismo
from .models import Desconocido, usos, tipoDesc, tipo_finca
from django.db.models import F
from decimal import Decimal
import csv

def carga_usos():
    lista = [
        ('1', '????'),
        ('V', 'VIVIENDA'),
        ('J', 'INDUSTRIAL AGRARIO'),
        ('O', 'OFICINAS'),
        ('A', 'ALMACÉN'),
        ('I', 'INDUSTRIAL'),
        ('K', 'DEPORTIVO'),
        ('Z', 'AGRARIO'),
        ('M', 'SOLAR SIN CONSTRUCCIÓN'),
        ('R', 'RELIGIOSO'),
        ('C', 'COMERCIAL'),
        ('T', 'ESPECTÁCULOS'),
        ('G', 'OCIO Y HOSTELERÍA'),
        ('Y', 'SANIDAD Y BENEFICENCIA'),
        ('E', 'ENSEÑANZA'),
        ('P', 'EDIFICIOS SINGULARES')
    ]
    for clave, descripcion in lista:
        try:
            a = usos(clave=clave, descripcion=descripcion)
            a.save()
        except Exception as ex:
            print(clave, ex)


def carga_ti():
    with open('desconocidos/TI.txt', newline='') as fichero:
        lector = csv.reader(fichero, delimiter=';')
        for row in lector:
            org = int(row[1])//1000
            codigo = int(row[1][-3:])
            nombre = row[2]
            ti = float(row[3].replace(',', '.'))
            ti_ru = float(row[4].replace(',', '.'))
            delegacion = organismo.objects.get(cod=org)
            try:
                q = municipio(cod=codigo, nombre=nombre, tipo_impositivo=ti, tipo_impositivo_ru=ti_ru, org=delegacion)
                q.save()
                print(delegacion, codigo, nombre, ti, ti_ru)
            except Exception as err:
                if 'Ya existe la llave' in err.__str__():
                    q = municipio.objects.get(cod=codigo, org=delegacion)
                    q.tipo_impositivo = ti
                    q.tipo_impositivo_ru = ti_ru
                    q.save()
                    print(delegacion, codigo, nombre, ti, ti_ru)

def clasifica():
    desc = Desconocido.objects.all()
    tipo_antiecon = tipoDesc.objects.get(descripcion='ANTIECONÓMICO')
    tipo_investigable = tipoDesc.objects.get(descripcion='INVESTIGABLE')
    tipo_rustica = tipoDesc.objects.get(descripcion='RÚSTICA SOLAR')
    tipo_solar = tipoDesc.objects.get(descripcion='URBANA SOLAR')
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
    i = 0
    for desco in antieconomicos:
        desco.tipo = tipo_antiecon
        desco.save()
        print(desco, tipo_antiecon)
        i += 1
    for desco in rusticas:
        desco.tipo = tipo_rustica
        desco.save()
        print(desco, tipo_rustica)
        i += 1
    for desco in solares:
        desco.tipo = tipo_solar
        desco.save()
        print(desco, tipo_solar)
        i += 1
    for desco in investigables:
        desco.tipo = tipo_investigable
        desco.save()
        print(desco, tipo_investigable)
        i += 1
    print(str(i)+'/'+str(desc.count()))

def cargaDesc():
    tipo_antiecon = tipoDesc.objects.get(descripcion='ANTIECONÓMICO')
    tipo_investigable = tipoDesc.objects.get(descripcion='INVESTIGABLE')
    tipo_rustica = tipoDesc.objects.get(descripcion='RÚSTICA SOLAR')
    tipo_solar = tipoDesc.objects.get(descripcion='URBANA SOLAR')
    with open('desconocidos/desconocidos.txt', newline='') as fichero:
        lector = csv.reader(fichero, delimiter=';')
        i = 0
        muni_fallidos = []
        filas = 0
        for row in lector:
            filas += 1
            try:
                cod_delegacion = int(row[0])//1000
                muni = municipio.objects.get(org__cod=cod_delegacion, cod=row[0][-3:])
                if row[22] == '':
                    uso = usos.objects.get(pk='1')
                else:
                    uso = usos.objects.get(pk=row[22])

                q = Desconocido(
                    fk_muni=muni,
                    refcat=row[2],
                    num_fijo=row[3],
                    sigla_via=row[5],
                    nombre_via=row[6],
                    num_pol=row[7],
                    letra_pol=row[8],
                    num_pol_2=row[9],
                    letra_pol_2=row[10],
                    escalera=row[13],
                    planta=row[14],
                    puerta=row[15],
                    dir_no_estruc=row[16],
                    cod_postal=row[17],
                    v_cat=int(row[18].replace(',00', '')),
                    v_suelo=int(row[19].replace(',00', '')),
                    v_constru=int(row[20].replace(',00', '')),
                    b_liquidable=int(row[21].replace(',00', '')),
                    clave_uso=uso,
                    id_fiscal=row[23],
                    sujeto_pasivo=row[24],
                )

                if q.num_fijo == '':
                    clase = 'RÚSTICA'
                else:
                    clase = 'URBANA'
                q.tipo_finca = tipo_finca.objects.get(descripcion=clase)
                if q.tipo_finca.descripcion == 'URBANA':
                    q.cuota = round(
                        Decimal((q.b_liquidable / 100)) * q.fk_muni.tipo_impositivo / 100, 2)

                else:
                    q.cuota = round(
                        Decimal((q.b_liquidable / 100)) * q.fk_muni.tipo_impositivo_ru / 100, 2)

                if q.cuota < q.fk_muni.org.antieconomico:
                    q.tipo = tipo_antiecon
                elif q.tipo_finca.descripcion == 'RÚSTICA' and q.v_constru == 0:
                    q.tipo = tipo_rustica
                elif q.tipo_finca.descripcion == 'URBANA' and q.v_constru == 0:
                    q.tipo = tipo_solar
                else:
                    q.tipo = tipo_investigable


                q.save()
                print('Cargado desconocido: ' + row[2])
                i += 1

            except Exception as err:

                muni_inexistente = (str(int(row[0])//1000), row[0][-3:], row[1], row[2], err)
                if muni_inexistente not in muni_fallidos:
                    muni_fallidos.append(muni_inexistente)

        print('Cargados ' + str(i) + '/' + str(filas) + ' desconocidos.')
        print('----- LOS SIGUIENTES DESCONOCIDOS NO HAN CARGADO -----')
        for deleg, cod_muni, nombre, finca, error in muni_fallidos:
            print(deleg, cod_muni, nombre, finca, error)

def actCuota():
    lista = Desconocido.objects.all()
    for desconocido in lista:
        if desconocido.tipo_finca.descripcion == 'URBANA':
            desconocido.cuota = round(Decimal((desconocido.b_liquidable / 100)) * desconocido.fk_muni.tipo_impositivo / 100, 2)
            print(desconocido.refcat, 'URBANA')
        else:
            desconocido.cuota = round(
                Decimal((desconocido.b_liquidable / 100)) * desconocido.fk_muni.tipo_impositivo_ru / 100, 2)
            print(desconocido.refcat, 'RÚSTICA')
        desconocido.save()

def actNaturaleza():
    lista = Desconocido.objects.all()
    i = 0
    for desconocido in lista:
        i += 1
        if desconocido.num_fijo == '':
            desconocido.tipo_finca = tipo_finca.objects.get(descripcion='RÚSTICA')
        else:
            desconocido.tipo_finca = tipo_finca.objects.get(descripcion='URBANA')
        print(str(i)+'/'+str(lista.count()))
        desconocido.save()


def ti_ru():
    with open('desconocidos/TI.txt', newline='') as fichero:
        lector = csv.reader(fichero, delimiter=';')
        for row in lector:
            org = int(row[1])//1000
            codigo = int(row[1][-3:])
            nombre = row[2]
            ti = float(row[3].replace(',', '.'))
            delegacion = organismo.objects.get(cod=org)
            try:
                q = municipio.objects.filter(cod=codigo, org=delegacion).first()
                q.tipo_impositivo_ru = ti
                q.save()
            except:
                q = municipio(cod=codigo, nombre=nombre, tipo_impositivo_ru=ti, org=delegacion)
                q.save()
            print(q)

def ti_ur():
    with open('desconocidos/TI.txt', newline='') as fichero:
        lector = csv.reader(fichero, delimiter=';')
        for row in lector:
            org = int(row[1])//1000
            codigo = int(row[1][-3:])
            nombre = row[2]
            ti = float(row[3].replace(',', '.'))
            delegacion = organismo.objects.get(cod=org)
            try:
                q = municipio.objects.filter(cod=codigo, org=delegacion).first()
                q.tipo_impositivo = ti
                q.save()
            except:
                q = municipio(cod=codigo, nombre=nombre, tipo_impositivo=ti, org=delegacion)
                q.save()
            print(q)

def loadDesc():
    cargaDesc()
    actNaturaleza()
    actCuota()


