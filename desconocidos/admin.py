from django.contrib import admin
from .models import Desconocido, actuaciones, tipoDesc, usos
from django.db.models import F
from decimal import Decimal

class actuacionesInLine(admin.StackedInline):
    model = actuaciones
    extra = 1

class ActuacionesAdmin(admin.ModelAdmin):
    list_display = ('desco', 'user', 'fecha')
    list_display_links = ('desco',)
    search_fields = ('desconocido__refcat',)

    def desco(self, obj):
        return obj.desconocido.refcat
    desco.short_description = "Desconocido"

    def user(self, obj):
        return obj.usuario.first_name + ' ' + obj.usuario.last_name
    user.short_description = "Usuario"


class DesconocidoAdmin(admin.ModelAdmin):
    list_display = ('delegacion', 'muni', 'refcat', 'cuota_ibi', 'resuelto')
    list_filter = ('fk_muni__org__nombre',)
    list_display_links = ('refcat',)
    search_fields = ('fk_muni__nombre', 'fk_muni__org__nombre', 'refcat')
    inlines = [actuacionesInLine, ]

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

admin.site.register(actuaciones, ActuacionesAdmin)
admin.site.register(tipoDesc)
admin.site.register(usos, UsosAdmin)
