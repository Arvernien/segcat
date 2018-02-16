from django.contrib import admin
from .models import Desconocido, actuaciones, tipoDesc, usos
from django.db.models import F
from decimal import Decimal

class DesconocidoAdmin(admin.ModelAdmin):
    list_display = ('delegacion', 'muni', 'refcat', 'cuota_ibi', 'resuelto')
    list_filter = ('fk_muni__org__nombre',)
    list_display_links = ('refcat',)
    search_fields = ('fk_muni__nombre', 'fk_muni__org__nombre', 'refcat')

    def get_queryset(self, request):
        qs = super(DesconocidoAdmin, self).get_queryset(request)
        qs = qs.order_by(((F('b_liquidable')/100) * F('fk_muni__tipo_impositivo')/100).desc())
        return qs

    def muni(self, obj):
        return obj.fk_muni
    muni.short_description = "MUNICIPIO"

    def delegacion(self, obj):
        return obj.fk_muni.org.nombre
    delegacion.short_description = "DELEGACIÓN"

    def cuota_ibi(self, obj):
        return str(round(Decimal((obj.b_liquidable/100)) * obj.fk_muni.tipo_impositivo / 100, 2)) + ' €'
    cuota_ibi.short_description = "CUOTA IBI"

class UsosAdmin(admin.ModelAdmin):
    list_display = ('clave', 'descripcion')
    list_display_links = ('descripcion',)
    search_fields = ('descripcion',)

# Register your models here.
admin.site.register(Desconocido, DesconocidoAdmin)
admin.site.register(actuaciones)
admin.site.register(tipoDesc)
admin.site.register(usos, UsosAdmin)
