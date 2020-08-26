from django import template
from django.db.models import Q

from ..models import FreeAgent, OtherEvents, Team, Player, Goal, Match, Substitution
from django.utils import timezone

register = template.Library()


@register.filter
def user_in_agents(user):
    try:
        a = FreeAgent.objects.get(player=user, is_active=True)
        return True
    except:
        return False


@register.filter
def can_add_entry(user):
    try:
        if timezone.now() - user.user_free_agent.created > timezone.timedelta(hours=6):
            return True
        else:
            return False
    except:
        return True


@register.filter
def date_can(user):
    return user.user_free_agent.created + timezone.timedelta(hours=6)


@register.filter
def event_count(player, type):
    return OtherEvents.objects.filter(author=player, team=player.team, event=type).count()


@register.filter
def goals_in_team(player, team):
    return Goal.objects.filter(author=player, team=team).count()

@register.filter
def assists_in_team(player, team):
    return Goal.objects.filter(assistent=player, team=team).count()

@register.filter
def replaced_in_team(player, team):
    return Substitution.objects.filter(team=team, player_out=player).count()

@register.filter
def join_game_in_team(player, team):
    return Substitution.objects.filter(team=team, player_in=player).count()

@register.filter
def matches_in_team(player, team):
    print(Match.objects.filter(team_guest=team, team_guest_start=player))
    print(Match.objects.filter(team_home=team, team_home_start=player))
    return Match.objects.filter(team_guest=team, team_guest_start=player).count() + Match.objects.filter(
        team_home=team, team_home_start=player).count()
# return Match.objects.filter(Q(team_home=team, team_home_start=player) | Q(team_guest=team, team_guest_start=player)).count()
