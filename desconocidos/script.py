from polls.models import municipio, organismo
from .models import Desconocido
import csv

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
                print(row[2])
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
                    clave_uso=row[22],
                    id_fiscal=row[23],
                    sujeto_pasivo=row[24]
                )
                q.save()
                print(muni)
                i += 1

            except:

                muni_inexistente = (str(int(row[0])//1000), row[0][-3:], row[1])
                if muni_inexistente not in muni_fallidos:
                    muni_fallidos.append(muni_inexistente)

        print('Cargados ' + str(i) + '/' + str(filas) + ' desconocidos.')
        print('----- LOS SIGUIENTES MUNICIPIOS NO EXISTEN ------')
        for deleg, cod_muni, nombre in muni_fallidos:
            print(deleg, cod_muni, nombre)

