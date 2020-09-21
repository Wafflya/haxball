from django import template
from django.db.models import Q, Count
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
        team_home=team, team_home_start=player).count() + Match.objects.filter(
        ~(Q(team_guest_start=player) | Q(team_home_start=player)), match_substitutions__team=team,
        match_substitutions__player_in=player
        ).distinct().count()


# return Match.objects.filter(Q(team_home=team, team_home_start=player) | Q(team_guest=team, team_guest_start=player)).count()

#   Для детальной статы матча


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
#   и теги
@register.inclusion_tag('tournament/include/cup_table.html')
def cup_table(league):
    return {'league': league}


@register.filter
def pairs_in_round(tour):
    matches = Match.objects.filter(numb_tour=tour)
    pairs = []
    for m in matches:
        pair = set()
        pair.add(m.team_home)
        pair.add(m.team_guest)
        if pair not in pairs:
            pairs.append(pair)
    pi = []
    for p in pairs:
        pi.append(list(p))
    print(pi)
    return pi


@register.filter
def round_name(tour, all_tours):
    if tour == all_tours:
        return 'Финал'
    elif tour == all_tours-1:
        return '1/2 Финала'
    elif tour == all_tours-2:
        return '1/4 Финала'
    elif tour == all_tours-3:
        return '1/8 Финала'
    else:
        return '{} Раунд'.format(tour)


@register.inclusion_tag('tournament/include/league_table.html')
def league_table(league):
    b = list(Team.objects.filter(leagues=league))
    c = len(b)
    points = [0 for _ in range(c)]  # Количество очков
    diffrence = [0 for _ in range(c)]  # Разница мячей
    scores = [0 for _ in range(c)]  # Мячей забито
    consided = [0 for _ in range(c)]  # Мячей пропущено
    matches_played = [0 for _ in range(c)]  # Игр сыграно
    wins = [0 for _ in range(c)]  # Побед
    draws = [0 for _ in range(c)]  # Ничей
    looses = [0 for _ in range(c)]  # Поражений
    last_matches = [[] for _ in range(c)]
    for i, team in enumerate(b):
        matches = Match.objects.filter((Q(team_home=team) | Q(team_guest=team)), league=league, is_played=True)
        matches_played[i] = matches.count()
        # last_matches[i] = [(m, 0) for m in matches]
        win_count = 0
        draw_count = 0
        loose_count = 0
        goals_scores_all = 0
        goals_consided_all = 0
        for m in matches:

            if team == m.team_home:
                score_team = m.score_home
                score_opp = m.score_guest
            elif team == m.team_guest:
                score_team = m.score_guest
                score_opp = m.score_home
            else:
                return None

            goals_scores_all += score_team
            goals_consided_all += score_opp

            if score_team > score_opp:
                win_count += 1
                last_matches[i].append((m, 1))
            elif score_team == score_opp:
                draw_count += 1
                last_matches[i].append((m, 0))
            else:
                loose_count += 1
                last_matches[i].append((m, -1))

        last_matches[i] = last_matches[i][-5:]
        points[i] = win_count * 3 + draw_count * 1
        diffrence[i] = goals_scores_all - goals_consided_all
        scores[i] = goals_scores_all
        consided[i] = goals_consided_all
        wins[i] = win_count
        looses[i] = loose_count
        draws[i] = draw_count

    l = zip(b, matches_played, wins, draws, looses, scores, consided, diffrence, points, last_matches)
    s1 = sorted(l, key=lambda x: x[5], reverse=True)
    s2 = sorted(s1, key=lambda x: x[7], reverse=True)
    ls = sorted(s2, key=lambda x: x[8], reverse=True)
    return {'teams': ls}


# Конец тегов и фильтров для таблицы лиги


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
    return Match.objects.filter((Q(team_home=team) | Q(team_guest=team)), league=league).order_by('numb_tour')
