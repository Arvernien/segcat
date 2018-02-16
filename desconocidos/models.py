from django.db import models
from polls.models import organismo, municipio
from django.contrib.auth.models import User


# Create your models here.

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
    fk_muni = models.ForeignKey(municipio, on_delete=models.DO_NOTHING)
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

    def creaActuacion(self, user, descr):
        q = actuaciones(desconocido=self, usuario=user, descripcion=descr)
        q.save()

    def __str__(self):
        return self.refcat

    class Meta:
        unique_together = (('fk_muni', 'refcat'),)

class actuaciones(models.Model):
    desconocido = models.ForeignKey(Desconocido, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    descripcion = models.CharField(max_length=400)

    class Meta:
        verbose_name_plural = 'Actuaciones'
