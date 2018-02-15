from django.db import models
from django.contrib.auth.models import Group
from django.core.validators import MaxValueValidator
from django.utils import timezone
import datetime

class organismo(models.Model):
    cod = models.IntegerField(validators=[MaxValueValidator(99),])
    nombre = models.CharField(max_length=100)
    grupo = models.ForeignKey(Group, on_delete=models.DO_NOTHING, default='')

    def __str__(self):
        return self.nombre

class municipio(models.Model):
    cod = models.IntegerField()
    nombre = models.CharField(max_length=100)
    tipo_impositivo = models.DecimalField(max_digits=4, decimal_places=3, blank=True, null=True)
    org = models.ForeignKey(organismo, on_delete=models.DO_NOTHING)

    class Meta:
        unique_together = (('org', 'cod'),)

    def __str__(self):
        return self.cod.__str__() + '\t - ' + self.nombre

    def codigo(self):
        return self.org.cod * 1000 + self.cod

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('fecha de publicación')

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now
    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text

TIPOS = (
    ('PROPIA', 'PROPIA'),
    ('AFECTADA', 'AFECTADA'),
    ('GRÁFICO', 'GRÁFICO'),
)

class Finca(models.Model):
    refcat = models.CharField(max_length=14)
    TipoFinca = models.CharField(max_length=20, choices=TIPOS, default='PROPIA')
    def __str__(self):
        return self.refcat