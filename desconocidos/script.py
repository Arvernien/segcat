from polls.models import municipio, organismo
from .models import Desconocido, usos, tipoDesc, tipo_finca
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

            delegacion = organismo.objects.get(cod=org)
            try:
                q = municipio(cod=codigo, nombre=nombre, tipo_impositivo=ti, org=delegacion)
                q.save()
                print(delegacion, codigo, nombre, ti)
            except:
                print('Ya existe: ', codigo, nombre)

def cargaDesc():
    with open('desconocidos/desconocidos.txt', newline='') as fichero:
        lector = csv.reader(fichero, delimiter=';')
        i = 0
        muni_fallidos = []
        filas = 0
        for row in lector:
            filas += 1
            try:
                delegacion = organismo.objects.get(cod=int(row[0])//1000)
                muni = municipio.objects.get(org=delegacion, cod=row[0][-3:])
                if row[22] == '':
                    uso = usos.objects.get(pk='1')
                else:
                    uso = usos.objects.get(pk=row[22])
                if 'EN INVESTIGACION' in row[24]:
                    tipo = tipoDesc.objects.get(descripcion='EN INVESTIGACIÓN')
                else:
                    tipo = tipoDesc.objects.get(descripcion='NIF FICTICIO')

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
                    v_cat=int(row[18]),
                    v_suelo=int(row[19]),
                    v_constru=int(row[20]),
                    b_liquidable=int(row[21]),
                    clave_uso=uso,
                    id_fiscal=row[23],
                    sujeto_pasivo=row[24],
                    tipo= tipo
                )
                q.save()
                print('Cargado desconocido: ' +row[2])
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
        desconocido.cuota = round(Decimal((desconocido.b_liquidable / 100)) * desconocido.fk_muni.tipo_impositivo / 100, 2)
        desconocido.save()

def actNaturaleza():
    lista = Desconocido.objects.all()
    for desconocido in lista:
        # codmuni = str((desconocido.fk_muni.org.cod * 1000) + (desconocido.fk_muni.cod))
        # if len(codmuni) < 5:
        #     codmuni = '0' + codmuni
        #
        refcat = desconocido.refcat[:14]
        dgfparcela = refcat[:7]
        dgfhoja = refcat[-7:]
        try:
            a = int(dgfhoja)
            clase = 'RÚSTICA'
        except:
            clase = 'URBANA'
        desconocido.tipo_finca = tipo_finca.objects.get(descripcion=clase)
        desconocido.save()
        print(desconocido.refcat + '-->' + clase)

