from datetime import timedelta
from datetime import time

from django import template
from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from django.db.models.functions import datetime
from django.utils import timezone
from tournament.models import Player, Team, League, TourNumber, Match
from ..models import ReservationEntry

register = template.Library()


def teams_can_reserv(user):
    try:
        a = user.user_player
    except:
        return False
    t = []
    if a.role == 'C' or a.role == 'AC':
        t.append(a.team)

    tt = Team.objects.filter(owner=user)
    active_teams = Team.objects.filter(leagues__championship__is_active=True)
    for i in tt:
        if i in active_teams:
            t.append(i)

    return t


@register.filter
def user_can_reserv(user):
    if teams_can_reserv(user):
        return True
    else:
        return False


@register.inclusion_tag('reservation/reservation_form.html')
def reservation_form(user):
    t = teams_can_reserv(user)
    actual_tour = TourNumber.objects.filter(league__championship__is_active=True, is_actual=True).first()

    matches_unplayed = Match.objects.filter((Q(team_home__in=t) | Q(team_guest__in=t)), is_played=False,
                                            numb_tour__number__lte=actual_tour.number,
                                            ).order_by('-numb_tour__number')
    matches_to_choose = []

    for m in matches_unplayed:
        try:
            a = m.match_reservation
        except:
            matches_to_choose.append(m)

    date_today = datetime.datetime.today()
    d = date_today + timedelta(minutes=5)
    time_end = datetime.datetime(year=actual_tour.date_to.year, month=actual_tour.date_to.month,
                                 day=actual_tour.date_to.day, hour=23, minute=30, second=0)

    return {
        'matches': matches_to_choose,
        'date_today': d,
        'time_end': time_end,
        'user': user,
    }


@register.filter
def match_can_delete(user, match):
    if user.is_anonymous:
        return False
    try:
        a = user.user_player
    except:
        return False
    t = teams_can_reserv(user)
    delt_time = match.match_reservation.time_date - timezone.now()
    if ((match.team_home in t) or (match.team_guest in t)) and delt_time > timedelta(minutes=30):
        return True
    else:
        return False


@register.filter
def match_dates(reserved):
    datess = set()
    for i in reserved:
        datess.add(i.time_date.date())
    # dats = [datess]
    return sorted(datess)


@register.filter
def cols_span(hosts):
    return round(100 / hosts)


@register.filter
def date_equal(date, day):
    if date.date() == day:
        return True
    else:
        return False


@register.filter
def round_name(tour, all_tours):
    if tour == all_tours:
        return 'Финал'
    elif tour == all_tours - 1:
        return '1/2 Финала'
    elif tour == all_tours - 2:
        return '1/4 Финала'
    elif tour == all_tours - 3:
        return '1/8 Финала'
    else:
        return '{} Раунд'.format(tour)


'''
@register.filter
def match_can_reserv(user):
    t = teams_can_reserv(user)
    actual_tour = TourNumber.objects.filter(league__championship__is_active=True, is_actual=True).first()

    matches_unplayed = Match.objects.filter((Q(team_home__in=t) | Q(team_guest__in=t)), is_played=False,
                                            numb_tour__number__lte=actual_tour.number,
                                            )
    return matches_unplayed
'''
