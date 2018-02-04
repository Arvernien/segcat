from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from .models import Choice, Question, Finca
from django.views import generic


class CrearFinca(generic.CreateView):
    model = Finca
    fields = ['refcat', 'TipoFinca']

class FincaView(generic.ListView):
    template_name = 'polls/finca.html'
    context_object_name = 'fincas'

    def get_queryset(self):
        return Finca.objects.all()

class LoginView(generic.View):
    template_name = 'polls/auth.html'

    def __get__(self):
        return

class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]


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



# Create your views here.
