from django.db import models
from polls.models import organismo, municipio
from django.contrib.auth.models import User


# Create your models here.
class Desconocido(models.Model):
    fk_muni = models.ForeignKey(municipio, on_delete=models.DO_NOTHING)
    refcat = models.CharField(max_length=20)
    num_fijo = models.CharField(max_length=14)
    sigla_via = models.CharField(max_length=5)
    nombre_via = models.CharField(max_length=100)
    num_pol = models.CharField(max_length=4)
    letra_pol = models.CharField(max_length=1)
    num_pol_2 = models.CharField(max_length=4)
    letra_pol_2 = models.CharField(max_length=1)
    escalera = models.CharField(max_length=2)
    planta = models.CharField(max_length=3)
    puerta = models.CharField(max_length=5)
    dir_no_estruc = models.CharField(max_length=25)
    cod_postal = models.CharField(max_length=5)
    v_cat = models.IntegerField()
    v_suelo = models.IntegerField()
    v_constru = models.IntegerField()
    b_liquidable = models.IntegerField()
    clave_uso = models.CharField(max_length=25)
    id_fiscal = models.CharField(max_length=10)
    sujeto_pasivo = models.CharField(max_length=60)

class actuacion(models.Model):
    desconocido = models.ForeignKey(Desconocido, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    descripcion = models.CharField(max_length=400)
