from django import template
from django.db.models import Q, Count, Max
from django.utils import timezone

from ..models import FreeAgent, OtherEvents, Goal, Match, League, Team, Player, Substitution

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
    return Match.objects.filter(team_guest=team, team_guest_start=player).count() + Match.objects.filter(
        team_home=team, team_home_start=player).count() + Match.objects.filter(match_substitutions__team=team,
                                                                               match_substitutions__player_in=player, ).distinct().count()


# return Match.objects.filter(Q(team_home=team, team_home_start=player) | Q(team_guest=team, team_guest_start=player)).count()

#   Для детальной статы матча
@register.filter
def team_goals_in_match(match, team):
    if team == match.team_home:
        return Goal.objects.filter(match=match, team=team).count() + OtherEvents.objects.filter(event='OG', match=match,
                                                                                                team=match.team_guest).count()
    elif team == match.team_guest:
        return Goal.objects.filter(match=match, team=team).count() + OtherEvents.objects.filter(event='OG', match=match,
                                                                                                team=match.team_home).count()


@register.filter
def goals_sorted(match):
    events = match.match_event.all()
    substit = match.match_substitutions.all()
    goals = list(match.match_goal.all())
    for e in events:
        goals.append(e)
    for s in substit:
        goals.append(s)
    g1 = sorted(goals, key=lambda time: time.time_sec)
    g2 = sorted(g1, key=lambda time: time.time_min)
    return g2


#   Фильтры для таблички лиги
@register.filter
def matches_in_league(team):
    try:
        league = League.objects.get(is_cup=False, championship__is_active=True, priority=1)
    except:
        return None
    return Match.objects.filter(team_guest=team, league=league, is_played=True).count() + Match.objects.filter(
        team_home=team, league=league, is_played=True).count()


@register.filter
def res_in_league(team, res):
    try:
        league = League.objects.get(is_cup=False, championship__is_active=True, teams=team)
    except:
        return None
    matches = Match.objects.filter((Q(team_home=team) | Q(team_guest=team)), league=league, is_played=True)

    win_count = 0
    draw_count = 0
    loose_count = 0
    goals_scores_all = 0
    goals_consided_all = 0
    for m in matches:
        score_team = 0
        score_opp = 0
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
        goals_scores_all += score_team
        goals_consided_all += score_opp
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
    elif res == 's':
        return goals_scores_all
    elif res == 'c':
        return goals_consided_all
    elif res == 'dif':
        return goals_scores_all - goals_consided_all
    elif res == 'p':
        return win_count * 3 + draw_count * 1


@register.filter
def sort_teams(league):
    b = list(Team.objects.filter(leagues=league))
    points = [0 for _ in range(len(b))]
    diffrence = [0 for _ in range(len(b))]
    scores = [0 for _ in range(len(b))]
    for i, team in enumerate(b):
        matches = Match.objects.filter((Q(team_home=team) | Q(team_guest=team)), league=league, is_played=True)
        win_count = 0
        draw_count = 0
        loose_count = 0
        goals_scores_all = 0
        goals_consided_all = 0
        for m in matches:
            score_team = 0
            score_opp = 0
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

            goals_scores_all += score_team
            goals_consided_all += score_opp

            if score_team > score_opp:
                win_count += 1
            elif score_team == score_opp:
                draw_count += 1
        points[i] = win_count * 3 + draw_count * 1
        diffrence[i] = goals_scores_all - goals_consided_all
        scores[i] = goals_scores_all

    l = zip(b, points, diffrence, scores)

    s1 = sorted(l, key=lambda x: x[3], reverse=True)
    s2 = sorted(s1, key=lambda x: x[2], reverse=True)
    ls = sorted(s2, key=lambda x: x[1], reverse=True)
    lit = [i[0] for i in ls]
    queryset = lit
    return queryset


@register.filter
def top_goalscorers(league):
    players = Player.objects.filter(goals__match__league=league).annotate(
        goals_c=Count('goals__match__league')).order_by('-goals_c')
    return players


@register.filter
def top_assistent(league):
    players = Player.objects.filter(assists__match__league=league).annotate(
        ass_c=Count('assists__match__league')).order_by('-ass_c')
    return players


@register.filter
def top_clean_sheets(league):
    players = Player.objects.filter(event__match__league=league, event__event='CLN').annotate(
        event_c=Count('event__match__league')).order_by('-event_c')
    return players


#  Капитан и ассистент для профиля команды(контактов)
@register.filter
def get_captain(team):
    return Player.objects.filter(team=team, role='C')


@register.filter
def get_team_assistent(team):
    return Player.objects.filter(team=team, role='AC')


#       Получаем текущую "Лигу" команды
@register.filter
def current_league(team):
    return League.objects.filter(teams=team, championship__is_active=True, is_cup=False)


@register.filter
def current_position(team):
    leag = current_league(team).first()
    a = list(sort_teams(leag))
    return a.index(team) + 1


@register.filter
def teams_in_league_count(team):
    try:
        leag = current_league(team).first()
        return leag.teams.count()
    except:
        return '-'


@register.filter
def tour_matches_in_league(league, tour):
    return Match.objects.filter(league=league, tour_num=tour)


@register.filter
def team_matches_in_league(team, league):
    return Match.objects.filter((Q(team_home=team) | Q(team_guest=team)), league=league)
