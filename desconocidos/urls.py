from django.urls import path

from . import views

app_name = 'desconocidos'
urlpatterns = [
    path('', views.Desconocidos, name='desconocidos'),
    path('<int:pk>', views.detalle, name='detalle'),
]
