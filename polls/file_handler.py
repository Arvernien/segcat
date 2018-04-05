import pyodbc
from .models import municipio
from desconocidos.models import Desconocido, tipoDesc, tipo_finca, usos
from decimal import Decimal

def IdentificaFichero(ruta):
    tipo = 'NPI'
    if ruta[-3:] == 'mdb' or ruta[-5:] == 'accdb':
        conn_str = (
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            r'DBQ=' + ruta + ';'
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        for table_info in cursor.tables(tableType='TABLE'):
            if table_info.table_name == 'DESCONOCIDOS':
                tipo = 'DESCONOCIDOS'
    return tipo

def AccessDesconocidos(ruta):
    conn_str = (
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            r'DBQ=' + ruta + ';'
    )
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    sql = 'SELECT * FROM DESCONOCIDOS'
    cursor.execute(sql)
    rows = cursor.fetchall()
    filas = 0
    i = 0
    tipo_antiecon = tipoDesc.objects.get(descripcion='ANTIECONÓMICO')
    tipo_investigable = tipoDesc.objects.get(descripcion='INVESTIGABLE')
    tipo_rustica = tipoDesc.objects.get(descripcion='RÚSTICA SOLAR')
    tipo_solar = tipoDesc.objects.get(descripcion='URBANA SOLAR')
    tabla_cargados = ''
    tabla_errores = ''
    for row in rows:
        filas += 1
        try:
            cod_delegacion = int(row[0]) // 1000
            muni = municipio.objects.get(org__cod=cod_delegacion, cod=int(str(row[0])[-3:]))
            if row[22] == '':
                uso = usos.objects.get(pk='1')
            else:
                uso = usos.objects.get(pk=row[22])
            print(muni, uso)


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
                v_cat=row[18],
                v_suelo=row[19],
                v_constru=row[20],
                b_liquidable=row[21],
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
            tabla_cargados = ''.join(
                [tabla_cargados, '<tr><td>', q.refcat, '</td><td>', q.fk_muni.org.nombre, '</td><td>',
                 q.fk_muni.nombre,
                 '</td><td></tr>', '\n'])
            # print('Cargado desconocido: ' + row[2])
            i += 1

        except Exception as err:
            print(err)
            if 'duplicada' in err.__str__():
                tabla_errores = ''.join(
                    [tabla_errores, '<tr><td>', row[2], '</td><td>', muni.org.nombre, '</td><td>',
                     muni.nombre, '</td><td>', 'Ya existe el desconocido.', '</td></tr>', '\n'])
    tabla_cargados = ''.join(['<table class="table table-sm table-hover">'
                              '<thead>'
                              '<tr><th class="text-center" colspan="3">DESCONOCIDOS CARGADOS</th></tr>'
                              '<tr><th scope="col">Desconocido</th>'
                              '<th scope="col">Organismo</th>'
                              '<th scope="col">Municipio</th>'
                              '</tr>'
                              '</thead>', '\n', tabla_cargados, '\n', '</table>'])
    tabla_errores = ''.join(['<table class="table table-sm table-hover">'
                             '<thead>'
                             '<tr><th class="text-center" colspan="4">DESCONOCIDOS NO CARGADOS</th></tr>'
                             '<tr><th scope="col">Desconocido</th>'
                             '<th scope="col">Organismo</th>'
                             '<th scope="col">Municipio</th>'
                             '<th scope="col">Motivo</th>'
                             '</tr>'
                             '</thead>', '\n', tabla_errores, '\n', '</table>'])
    resultado = {
        'tabla_cargados': tabla_cargados,
        'tabla_errores': tabla_errores,
        'cargados': i,
        'totales': filas
    }
    conn.close()
    return resultado