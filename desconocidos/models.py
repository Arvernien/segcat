from django.db import models
from polls.models import organismo, municipio
from django.contrib.auth.models import User
from decimal import Decimal
import xml.etree.ElementTree as ET
import urllib.request
import datetime
from django.urls import reverse


# Create your models here.

class tipo_finca(models.Model):
    descripcion = models.CharField(max_length=15)

    def __str__(self):
        return self.descripcion

    class Meta:
        verbose_name_plural = "Tipos de finca"

class usos(models.Model):
    clave = models.CharField(max_length=25, primary_key=True)
    descripcion = models.CharField(max_length=25)

    def __str__(self):
        return self.descripcion +' (' + self.clave + ')'

    class Meta:
        verbose_name_plural = "Usos"

class tipoDesc(models.Model):
    descripcion = models.CharField(max_length=20)

    def __str__(self):
        return self.descripcion

    class Meta:
        verbose_name_plural = 'Tipos de desconocido'

class Desconocido(models.Model):
    fk_muni = models.ForeignKey(municipio, on_delete=models.DO_NOTHING, default='')
    refcat = models.CharField(max_length=20, blank=True)
    num_fijo = models.CharField(max_length=14, blank=True)
    sigla_via = models.CharField(max_length=5, blank=True)
    nombre_via = models.CharField(max_length=100, blank=True)
    num_pol = models.CharField(max_length=4, blank=True)
    letra_pol = models.CharField(max_length=1, blank=True)
    num_pol_2 = models.CharField(max_length=4, blank=True)
    letra_pol_2 = models.CharField(max_length=1, blank=True)
    escalera = models.CharField(max_length=2, blank=True)
    planta = models.CharField(max_length=3, blank=True)
    puerta = models.CharField(max_length=5, blank=True)
    dir_no_estruc = models.CharField(max_length=25, blank=True)
    cod_postal = models.CharField(max_length=5, blank=True)
    v_cat = models.IntegerField()
    v_suelo = models.IntegerField()
    v_constru = models.IntegerField()
    b_liquidable = models.IntegerField()
    clave_uso = models.ForeignKey(usos, on_delete=models.DO_NOTHING, default='1')
    id_fiscal = models.CharField(max_length=10, blank=True)
    sujeto_pasivo = models.CharField(max_length=60, blank=True)
    resuelto = models.BooleanField(default=False)
    tipo = models.ForeignKey(tipoDesc, on_delete=models.DO_NOTHING, default='1')
    titular_candidato = models.CharField(max_length=100, blank=True, null=True)
    nif_candidato = models.CharField(max_length=9, blank=True, null=True)
    expediente = models.CharField(max_length=14, blank=True, null=True)
    mt = models.BooleanField(blank=True, default=False)
    liq = models.BooleanField(blank=True, default=False)
    importe_liq = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, default=0)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    cuota = models.DecimalField(max_digits=15, decimal_places=2)
    tipo_finca = models.ForeignKey(tipo_finca, on_delete=models.DO_NOTHING, null=True, blank=True)


    def creaActuacion(self, user, descr, fecha, agendar):
        q = actuaciones(desconocido=self, usuario=user, descripcion=descr, agendar=agendar)
        q.save()

    def __str__(self):
        return self.refcat

    @property
    def getIbi(self):
        ibi = round(Decimal((self.b_liquidable/100)) * self.fk_muni.tipo_impositivo / 100, 2)
        return ibi

    @property
    def getDireccion(self):
        via = ' '.join([self.sigla_via, self.nombre_via, ])
        if self.num_pol != '0000':
            num = ' Nº ' + self.num_pol + self.letra_pol
        else:
            num = ''
        if self.num_pol_2 != '':
            num2 = 'Bis ' + self.num_pol_2 + self.letra_pol_2
        else:
            num2 = ''

        direninmueble = ''
        if self.escalera != '':
            direninmueble = 'ES: ' + self.escalera
        if self.planta != '':
            direninmueble = direninmueble + ' PL: ' + self.planta
        if self.puerta != '':
            direninmueble = direninmueble + ' PU: ' + self.puerta

        direccion = via
        if num != '':
            direccion = direccion + num
            if num2 != '':
                direccion = direccion + num2

        return ' '.join([direccion, direninmueble, ])

    @property
    def getVcat(self):
        vcat = round(Decimal(self.v_cat/100),2)
        return vcat

    @property
    def getVsuelo(self):
        vsuelo = round(Decimal(self.v_suelo / 100), 2)
        return vsuelo

    @property
    def getVcons(self):
        vcons = round(Decimal(self.v_constru / 100), 2)
        return vcons

    @property
    def getBliq(self):
        bliq = round(Decimal(self.b_liquidable / 100), 2)
        return bliq

    @property
    def getGmaps(self):
        try:
            url = 'http://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCoordenadas.asmx/' \
                  'Consulta_CPMRC?Provincia=&Municipio=&SRS=EPSG:4258&RC='
            urllib.request.urlopen(url)
            url = 'http://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCoordenadas.asmx/' \
                  'Consulta_CPMRC?Provincia=&Municipio=&SRS=EPSG:4258&RC=' + self.refcat[:14]
            tree = ET.parse(urllib.request.urlopen(url))
            root = tree.getroot()


            for a in root.iter():
                if a.tag == '{http://www.catastro.meh.es/}xcen':
                    xcen = str(round(float(a.text), 3))
                if a.tag == '{http://www.catastro.meh.es/}ycen':
                    ycen = str(round(float(a.text), 3))

            gmaps = '{lat: ' + ycen + ', lng: ' + xcen + '}'
            return gmaps
        except:
            return None

    @property
    def getCarto(self):
        url ='https://www1.sedecatastro.gob.es/Cartografia/mapa.aspx?refcat=' + self.refcat
        return url







    class Meta:
        unique_together = (('fk_muni', 'refcat'),)

class actuaciones(models.Model):
    desconocido = models.ForeignKey(Desconocido, on_delete=models.CASCADE, default='')
    usuario = models.ForeignKey(User, on_delete=models.DO_NOTHING, default='')
    fecha = models.DateTimeField(default=datetime.datetime.today)
    descripcion = models.CharField(max_length=400)
    agendar = models.DateField(null=True)
    revisado = models.BooleanField(default=False)

    def __str__(self):
        return self.desconocido.refcat

    class Meta:
        verbose_name_plural = 'Actuaciones'

    @property
    def get_absolute_url(self):
        return reverse('desconocidos:detalle', args=[str(self.desconocido.pk)])

    @property
    def get_link_name(self):
        return self.desconocido.refcat

class tipotramite(models.Model):
    descripcion = models.CharField(max_length=20, default='')

    def __str__(self):
        return self.descripcion

    class Meta:
        verbose_name_plural = 'Tipos de trámite'


class tramites(models.Model):
    desconocido = models.ForeignKey(Desconocido, on_delete=models.CASCADE, default='')
    usuario = models.ForeignKey(User, on_delete=models.DO_NOTHING, default='')
    fecha = models.DateTimeField(default=datetime.datetime.today)
    tipo = models.ForeignKey(tipotramite, on_delete=models.DO_NOTHING, default='')
    ampliacion = models.TextField(default='')

    class Meta:
        verbose_name_plural = 'Trámites'
