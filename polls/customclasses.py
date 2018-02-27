from calendar import LocaleHTMLCalendar
from desconocidos.models import actuaciones
from datetime import date
from itertools import groupby
from django.utils.html import conditional_escape as esc


class Agenda(LocaleHTMLCalendar):
    def __init__(self, events=None):
        super(Agenda, self).__init__()
        self.events = events
        self.locale = 'es-es'

    def formatday(self, day, weekday, events):
        """
        Return a day as a table cell.
        """
        events_from_day = events.filter(agendar__day=day)
        events_html = '<ul>'
        for event in events_from_day:
            events_html += '<li><a href="' + event.get_absolute_url + '">Desconocido</li>'
        events_html += "</ul>"

        if day == 0:
            return '<td width="150" height="120" class="noday">&nbsp;</td>'  # day outside month
        else:
            return '<td width="150" height="120" class="%s">%d%s</td>' % (self.cssclasses[weekday], day, events_html)

    def formatweek(self, theweek, events):

        s = ''.join(self.formatday(d, wd, events) for (d, wd) in theweek)
        return '<tr>%s</tr>' % s

    def formatmonth(self, theyear, themonth, user, withyear=True):

        events = actuaciones.objects.filter(agendar__month=themonth, usuario=user, revisado=False)


        v = []
        a = v.append
        #a('<table border="0" cellpadding="0" cellspacing="0" class="month">')
        a('<table style="margin: 0px auto;" class="table table-bordered month" border="0" cellpadding="0" cellspacing="0">')
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        for week in self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(week, events))
            a('\n')
        a('</table>')
        a('\n')
        return ''.join(v)
