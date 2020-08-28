from django import template
from django.db.models import Q
from django.utils import timezone

from ..models import FreeAgent, OtherEvents, Goal, Match, Substitution, League

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

#   Для детальной статы матча
@register.filter
def team_goals_in_match(match, team):
    if team == match.team_home:
        return Goal.objects.filter(match=match, team=team).count() + OtherEvents.objects.filter(event='OG',
                                                                                                team=match.team_guest).count()
    else:
        return Goal.objects.filter(match=match, team=team).count() + OtherEvents.objects.filter(event='OG',
                                                                                                team=match.team_home).count()


#   Фильтры для таблички лиги
@register.filter
def matches_in_league(team):
    try:
        league = League.objects.get(is_cup=False, championship__is_active=True)
    except:
        return None
    return Match.objects.filter(team_guest=team, league=league, is_played=True).count() + Match.objects.filter(
        team_home=team, league=league, is_played=True).count()


@register.filter
def res_in_league(team, res):
    try:
        league = League.objects.get(is_cup=False, championship__is_active=True)
    except:
        return None
    matches = Match.objects.filter((Q(team_home=team) | Q(team_guest=team)), league=league, is_played=True)
    score_team = 0
    score_opp = 0
    win_count = 0
    draw_count = 0
    loose_count = 0
    for m in matches:
        for g in m.match_goal.all():
            if g.team == team:
                score_team += 1
            else:
                score_opp += 1
        for og in m.match_event.filter(event='OG'):
            if og.team == team:
                score_opp += 1
            else:
                score_team += 1
        print(score_team, score_opp)
        if score_team > score_opp:
            win_count += 1
        elif score_team == score_opp:
            draw_count += 1
        else:
            loose_count += 1

    if res == 'w':
        return win_count
    elif res == 'd':
        return draw_count
    elif res == 'l':
        return loose_count
    elif res == 'p':
        return win_count * 3 + draw_count * 1
