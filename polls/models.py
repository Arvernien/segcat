from django.db import models
from django.contrib.auth.models import Group, User
from django.core.validators import MaxValueValidator
from django.utils import timezone
import datetime


class organismo(models.Model):
    cod = models.IntegerField(validators=[MaxValueValidator(99),])
    nombre = models.CharField(max_length=100)
    grupo = models.ForeignKey(Group, on_delete=models.DO_NOTHING, default='')
    antieconomico = models.DecimalField(max_digits=4, decimal_places=2)
    padron_ibi = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    padron_n_OT = models.IntegerField()

    def __str__(self):
        return self.nombre

class municipio(models.Model):
    cod = models.IntegerField()
    nombre = models.CharField(max_length=100)
    tipo_impositivo = models.DecimalField(max_digits=5, decimal_places=4, blank=True, null=True)
    tipo_impositivo_ru = models.DecimalField(max_digits=5, decimal_places=4, blank=True, null=True)
    org = models.ForeignKey(organismo, on_delete=models.DO_NOTHING)

    class Meta:
        unique_together = (('org', 'cod'),)

    def __str__(self):
        return self.cod.__str__() + '\t - ' + self.nombre

    def codigo(self):
        return self.org.cod * 1000 + self.cod

class SubidaFichero(models.Model):
    titulo = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100, default='')
    fecha_subida = models.DateField(default=datetime.datetime.today)
    usuario = models.ForeignKey(User, on_delete=models.DO_NOTHING, default='')
    fichero = models.FileField(upload_to='ficheros/')