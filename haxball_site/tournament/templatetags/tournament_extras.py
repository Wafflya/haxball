from django import template
from ..models import FreeAgent
from django.utils import timezone



register = template.Library()


@register.filter
def user_in_agents(user):
    try:
        a = FreeAgent.objects.get(player=user, is_active = True)
        return True
    except:
        return False

@register.filter
def can_add_entry(user):
    try:
        if timezone.now() - user.user_free_agent.created > timezone.timedelta(minutes=5):
            return True
        else:
            return False
    except:
        return True

@register.filter
def date_can(user):
    return user.user_free_agent.created + timezone.timedelta(minutes=5)