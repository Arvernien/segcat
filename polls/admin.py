from django.contrib import admin
from .models import Choice, Question, Finca, organismo, municipio

class ChoiceInLine(admin.TabularInline):
    model = Choice
    extra = 3

class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['question_text']}),
        ('Date information', {'fields': ['pub_date'], 'classes':['collapse']}),
    ]
    inlines = [ChoiceInLine]
    list_display = ('question_text', 'pub_date', 'was_published_recently')
    list_filter = ['pub_date']
    search_fields = ['question_text']

class municipioAdmin(admin.ModelAdmin):
    list_display = ('delegacion', 'codigo', 'nombre', 'tipo_impositivo', 'tipo_impositivo_ru', 'organismo')
    list_display_links = ('codigo', 'nombre')
    list_filter = ['org__nombre',]
    search_fields = ('cod', 'nombre')

    def organismo(self, obj):
        return obj.org
    organismo.short_description = "ORGANISMO"

    def codigo(self, obj):
        return obj.cod
    codigo.short_description = "CÓDIGO"

    def delegacion(self, obj):
        return obj.org.cod
    delegacion.short_description = "DELEGACIÓN"

class organismoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'grupo')
    list_display_links = ('nombre',)
    search_fields = ('cod', 'nombre')

    def codigo(self, obj):
        return obj.cod
    codigo.short_description = "CÓDIGO"



admin.site.register(Question, QuestionAdmin)
admin.site.register(Finca)
admin.site.register(organismo, organismoAdmin)
admin.site.register(municipio, municipioAdmin)


# Register your models here.
