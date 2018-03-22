from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.utils import timezone
from .models import Choice, Question, Finca, organismo
from django.views import generic
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.utils.safestring import mark_safe
from .customclasses import Agenda
import datetime
import calendar


class CrearFinca(generic.CreateView):
    model = Finca
    fields = ['refcat', 'TipoFinca']

class FincaView(generic.ListView):
    template_name = 'polls/finca.html'
    context_object_name = 'fincas'

    def get_queryset(self):
        return Finca.objects.all()

class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]
@login_required
def Inicio(request):
    usuario = User.objects.get(username=request.user)
    organismos = organismo.objects.filter(grupo__in=usuario.groups.all())
    context = {'organismos': organismos, }
    return render(request, 'polls/inicio.html', context)


def Logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('polls:login'))


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay de question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "you didn´t select a choice",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))

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
