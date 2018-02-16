from django import template
from django.contrib.auth.models import Group, User

register = template.Library()

@register.filter(name='enGrupo')
def enGrupo(User, nombre_grupo):
    grupo = Group.objects.get(name=nombre_grupo)
    return True if grupo in User.groups.all() else False