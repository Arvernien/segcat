from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings


from . import views

app_name = 'polls'
urlpatterns = [
    #path('', views.IndexView.as_view(), name='index'),

    # path('', auth_views.LoginView.as_view(template_name='polls/login.html'), name='login'),
    path('', auth_views.LoginView.as_view(template_name='polls/login.html'), name='login'),
    path('inicio/', views.Inicio, name='inicio'),
    path('logout/', views.Logout, name='logout'),
    path('agenda/', views.agenda, name='agenda'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
