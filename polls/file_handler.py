import pyodbc
from .models import municipio, organismo
from desconocidos.models import Desconocido, tipoDesc, tipo_finca, usos
from segcat.settings import BASE_DIR
from decimal import Decimal
from sys import platform
import jaydebeapi

def cnxnLinux(ruta):
    ucanaccess_jars = [
        ''.join([BASE_DIR,'/polls/static/polls/UCanAccess/lib/hsqldb.jar']),
        ''.join([BASE_DIR,'/polls/static/polls/UCanAccess/lib/commons-lang-2.6.jar']),
        ''.join([BASE_DIR,'/polls/static/polls/UCanAccess/lib/commons-logging-1.1.3.jar']),
        ''.join([BASE_DIR,'/polls/static/polls/UCanAccess/lib/jackcess-2.1.9.jar']),
        ''.join([BASE_DIR,'/polls/static/polls/UCanAccess/loader/ucanload.jar']),
        ''.join([BASE_DIR,'/polls/static/polls/UCanAccess/ucanaccess-4.0.3.jar'])
        ]

    classpath = ":".join(ucanaccess_jars)
    print(classpath)
    cnxn = jaydebeapi.connect(
        "net.ucanaccess.jdbc.UcanaccessDriver",
        "jdbc:ucanaccess://" + ruta + ";newDatabaseVersion=V2010",
        ["", ""],
        classpath
        )
    return cnxn

def cnxnWindows(ruta):
    conn_str = (
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        r'DBQ=' + ruta + ';'
    )
    cnxn = pyodbc.connect(conn_str)
    return cnxn

def IdentificaFichero(ruta):
    tipo = 'NPI'
    conn = ''
    if ruta[-3:] == 'mdb' or ruta[-5:] == 'accdb':
        if platform == 'windows':
            conn = cnxnWindows(ruta)
        else:
            conn = cnxnLinux(ruta)
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM DESCONOCIDOS')
            tipo = 'DESCONOCIDOS'
        except:
            pass
    conn.close()
    return tipo

def AccessDesconocidos(ruta):
    # REALIZA CONEXIÓN CON PYODBC AL FICHERO ACCESS PROPORCIONADO Y SELECCIONA
    # TODOS LOS DESCONOCIDOS EN LA TABLA DESCONOCIDOS
    if platform == 'windows':
        conn = cnxnWindows(ruta)
    else:
        conn = cnxnLinux(ruta)

    cursor = conn.cursor()
    sql = 'SELECT * FROM DESCONOCIDOS'
    cursor.execute(sql)
    rows = cursor.fetchall()

    # INICIALIZA LAS VARIABLES NECESARIAS Y LOS TIPOS DE DESCONOCIDO
    filas = 0
    i = 0
    tabla_cargados = ''
    tabla_errores = ''
    tipo_antiecon = tipoDesc.objects.get(descripcion='ANTIECONÓMICO')
    tipo_investigable = tipoDesc.objects.get(descripcion='INVESTIGABLE')
    tipo_rustica = tipoDesc.objects.get(descripcion='RÚSTICA SOLAR')
    tipo_solar = tipoDesc.objects.get(descripcion='URBANA SOLAR')

    # BUCLE QUE RECORRE LOS REGISTROS DEL ACCESS
    for row in rows:
        filas += 1
        cod_delegacion = int(row[0]) // 1000
        org = organismo.objects.filter(cod=cod_delegacion)
        # COMPRUEBA LA EXISTENCIA DEL ORGANISMO EN FUNCIÓN DEL CODIGO DE DELEGACIÓN
        # SI NO EXISTE GENERA LA LINEA CORRESPONDIENTE EN TABLA_ERRORES
        if len(org) == 0:
            print('No existe organismo')
            tabla_errores = ''.join(
            [tabla_errores, '<tr><td>', row[2], '</td><td>', 'Código delegación:'
            + str(cod_delegacion), '</td><td>', row[1], '</td><td>',
            'No existe organismo para el código de delegación.', '</td></tr>', '\n'])
        else:
            print('Existe organismo')
            # UNA VEZ COMPROBADA LA EXISTENCIA DEL ORGANISMO COMPRUEBA LA EXISTENCIA
            # DEL MUNICIPIO, SI NO EXISTE GENERA LA LINEA EN TABLA_ERRORES
            muni = municipio.objects.filter(org__cod=cod_delegacion, cod=int(str(row[0])[-3:]))
            if len(muni) == 0:
                print('No existe municipio')
                tabla_errores = ''.join([tabla_errores, '<tr><td>', row[2], '</td><td>', '</td><td>', row[1], '</td><td>', 'No existe municipio ', row[1], ' con código ', str(row[0])[-3:], '</td></tr>', '\n'])
            else:
                print('Existe municipio')
                # COMPRUEBA SI EXISTE EL DESCONOCIDO Y SU ESTADO Y SI CORRESPONDE LO VUELCA
                # EN TABLA_ERRORES
                q = Desconocido.objects.filter(refcat=row[2])
                if len(q) == 1:
                    print('Existe desconocido')
                    estado = ''
                    if q[0].fecha_finalizacion == None:
                        estado = 'investigación abierta'
                    else:
                        estado = 'investigación cerrada el ' + q.fecha_finalizacion
                    tabla_errores = ''.join([tabla_errores, '<tr><td>', row[2], '</td><td>', org[0].nombre, '</td><td>', row[1], '</td><td>', 'Ya existe el desconocido con ', estado, '</td></tr>', '\n'])
                else:
                    print('No existe desconocido')
                    print(row[21])
                    if row[21] == '':
                        uso = usos.objects.get(pk='1')
                    else:
                        uso = usos.objects.get(pk=row[21])

                    q = Desconocido(
                        fk_muni=muni[0],
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
                    # IDENTIFICA LA NATURALEZA DE LA FINCA CON LA EXISTENCIA DEL NUMERO FIJO
                    # Y CALCULA SU CUOTA
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

                    # CLASIFICA EL TIPO DE DESCONOCIDO
                    if q.cuota < q.fk_muni.org.antieconomico:
                        q.tipo = tipo_antiecon
                    elif q.tipo_finca.descripcion == 'RÚSTICA' and q.v_constru == 0:
                        q.tipo = tipo_rustica
                    elif q.tipo_finca.descripcion == 'URBANA' and q.v_constru == 0:
                        q.tipo = tipo_solar
                    else:
                        q.tipo = tipo_investigable

                    # SALVA EL DESCONOCIDO Y VUELCA EL RESULTADO EN TABLA_CARGADOS
                    q.save()
                    tabla_cargados = ''.join(
                        [tabla_cargados, '<tr><td>', q.refcat, '</td><td>', q.fk_muni.org.nombre, '</td><td>',
                         q.fk_muni.nombre,
                         '</td><td></tr>', '\n'])

                    i += 1
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
    cod_delegacion = int(rows[0][0]) // 1000
    cod_muni = int(str(rows[0][0])[-3:])
    muni = municipio.objects.filter(org__cod=cod_delegacion, cod=cod_muni)
    if len(muni) != 0:
        desconocidos_organismo = Desconocido.objects.filter(fk_muni__org=muni[0].org)
        for desco in desconocidos_organismo:
            sql = "SELECT * FROM DESCONOCIDOS WHERE [Referencia Catastral] LIKE '" + desco.refcat + "'"
            cursor.execute(sql)
            rows = cursor.fetchall()
            print(desco.refcat, len(rows))

    resultado = {
        'tabla_cargados': tabla_cargados,
        'tabla_errores': tabla_errores,
        'cargados': i,
        'totales': filas
    }
    conn.close()
    return resultado
