from polls.models import municipio, organismo
import csv

def lanza():
    with open('desconocidos/TI.txt', newline='') as fichero:
        lector = csv.reader(fichero, delimiter=';')
        for row in lector:
            org = int(row[1])//1000
            codigo = int(row[1][-3:])
            nombre = row[2]
            ti = float(row[3].replace(',', '.'))

            a = organismo.objects.get(cod=org)
            q = municipio(cod=codigo, nombre=nombre, tipo_impositivo=ti, org=a)
            q.save()
            print(a, codigo, nombre, ti)

