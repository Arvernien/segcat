from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.utils import timezone
from .models import organismo
from django.views import generic
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.utils.safestring import mark_safe
from .customclasses import Agenda
import datetime
import calendar




@login_required
def Inicio(request):
    usuario = User.objects.get(username=request.user)
    organismos = organismo.objects.filter(grupo__in=usuario.groups.all())
    context = {'organismos': organismos, }
    return render(request, 'polls/inicio.html', context)


def Logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('polls:login'))

@login_required
def agenda(request):
    usr = User.objects.get(username=request.user)
    datos = request.GET or None
    if datos:
        f = datos.get('f')
        partido = f.split('-')
        f = datetime.date(year=int(partido[0]), month=int(partido[1]), day=1)
    else:
        f = datetime.datetime.today()
    today = datetime.date(year=datetime.datetime.today().year, month=datetime.datetime.today().month, day=1)
    f = datetime.date(year=f.year, month=f.month, day=1)
    y = f.year
    m = f.month
    cal = Agenda().formatmonth(y, m, usr)
    previous_month = datetime.date(year=f.year, month=f.month, day=1)  # find first day of current month
    previous_month = previous_month - datetime.timedelta(days=1)  # backs up a single day
    previous_month = datetime.date(year=previous_month.year, month=previous_month.month,
                                   day=1)  # find first day of previous month

    last_day = calendar.monthrange(f.year, f.month)
    next_month = datetime.date(year=f.year, month=f.month, day=last_day[1])  # find last day of current month
    next_month = next_month + datetime.timedelta(days=1)  # forward a single day
    next_month = datetime.date(year=next_month.year, month=next_month.month,
                               day=1)  # find first day of next month
    context = {'calendario': mark_safe(cal),
                'mprevio': str(previous_month),
                'msiguiente': str(next_month),
                'today': str(today)
               }
    return render(request, 'polls/agenda.html', context)
