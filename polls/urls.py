from django.urls import path
from django.contrib.auth import views as auth_views


from . import views

app_name = 'polls'
urlpatterns = [
    #path('', views.IndexView.as_view(), name='index'),

    path('', auth_views.LoginView.as_view(template_name='polls/login.html'), name='login'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
    path('finca/', views.FincaView.as_view(), name='finca'),
    path('crea/', views.CrearFinca.as_view(), name='crea'),
]

