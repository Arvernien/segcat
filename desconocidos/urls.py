from django.urls import path

from . import views

app_name = 'desconocidos'
urlpatterns = [
    path('', views.Desconocidos, name='desconocidos'),
    path('busqstats/', views.busqstats, name='busqstats'),
    path('<int:pk>', views.detalle, name='detalle'),
    path('addnota', views.addnota, name='addnota'),
    path('addnotatest', views.addnotatest, name='addnotatest'),
    path('addtramite', views.addtramite, name='addtramite'),
    path('checknota', views.checknota, name='checknota'),
    path('checktram', views.checktramite, name='checktramite'),
    path('orgdatos', views.orgdatos, name='orgdatos'),
    path('datosform', views.grabadatos, name='datosform'),
    path('organismo/<int:pk>', views.orgstats, name='orgstats'),
    path('pdf', views.pdftest, name='pdf'),
    path('subir', views.subefichero, name='subir'),
    path('delfichero/<int:pk>', views.borrafichero, name='borrafichero'),
]
