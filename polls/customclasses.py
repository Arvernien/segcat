from calendar import LocaleHTMLCalendar
from desconocidos.models import actuaciones, tramites
from datetime import date
from itertools import groupby
from django.utils.html import conditional_escape as esc


class Agenda(LocaleHTMLCalendar):
    def __init__(self, acts=None):
        super(Agenda, self).__init__()
        self.acts = acts
        self.locale = 'es-es'

    def formatday(self, day, weekday, acts, trams, today):
        """
        Return a day as a table cell.
        """
        actuaciones = acts.filter(agendar__day=day)
        tramites = trams.filter(agendar__day=day)
        events_html = ''

        for event in actuaciones:
            #events_html += '<li class=""><a class="texto-peq" href="' + event.get_absolute_url + '">' + event.desconocido.refcat + '</li>'
            events_html += '<br><a class="texto-peq" href="' + event.get_absolute_url + \
                           '" data-toggle="tooltip" data-placement="bottom" title="Nota agendada">' + \
                           '<i class="fas fa-pencil-alt text-primary"></i> ' + event.desconocido.refcat
        for event in tramites:
            events_html += '<br><a class="texto-peq" href="' + event.get_absolute_url + '" data-toggle="tooltip" data-placement="bottom" title="' + event.tipo.descripcion + '">' + '<i class="' + \
                           str(event.tipo.icono).replace('fa-lg text-secondary', 'text-primary') + '"></i> ' + event.desconocido.refcat

        if day == 0:
            return '<td width="150" height="120" class="noday">&nbsp;</td>'  # day outside month
        else:
            if today and today.day == day:
                return '<td width="150" height="120" class="%s" style="background-color: rgb(224, 247, 212);">%d%s</td>' % (
                self.cssclasses[weekday], day, events_html)
            else:
                return '<td width="150" height="120" class="%s">%d%s</td>' % (self.cssclasses[weekday], day, events_html)

    def formatweek(self, theweek, acts, trams, today=None):

        s = ''.join(self.formatday(d, wd, acts, trams, today) for (d, wd) in theweek)
        return '<tr>%s</tr>' % s

    def formatmonth(self, theyear, themonth, user, withyear=True):

        acts = actuaciones.objects.filter(agendar__month=themonth, usuario=user, revisado=False)
        trams = tramites.objects.filter(agendar__month=themonth, usuario=user, revisado=False)
        today = date.today()
        if today.year != theyear or today.month != themonth:
            today = None

        v = []
        a = v.append
        a('<table style="margin: 0px auto;" class="table table-bordered month" border="0" cellpadding="0" cellspacing="0">')
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        for week in self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(week, acts, trams, today))
            a('\n')
        a('</table>')
        a('\n')
        return ''.join(v)
