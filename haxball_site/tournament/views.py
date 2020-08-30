from django.db.models import Count, F, Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import ListView, DetailView

from .forms import FreeAgentForm
from .models import FreeAgent, Team, Match, League, Player


class FreeAgentList(ListView):
    queryset = FreeAgent.objects.filter(is_active=True).order_by('-created')
    context_object_name = 'agents'
    template_name = 'tournament/free_agent/free_agents_list.html'

    def post(self, request):
        if request.method == 'POST':
            try:
                fa = FreeAgent.objects.get(player=request.user)
                fa_form = FreeAgentForm(data=request.POST, instance=fa)
                if fa_form.is_valid():
                    fa = fa_form.save(commit=False)
                    fa.created = timezone.now()
                    fa.is_active = True
                    fa.save()
                    agents = FreeAgent.objects.filter(is_active=True).order_by('-created')
                    return redirect('tournament:free_agent')
            except:
                fa_form = FreeAgentForm(data=request.POST)
                if fa_form.is_valid():
                    fa = fa_form.save(commit=False)
                    fa.player = request.user
                    fa.created = timezone.now()
                    fa.is_active = True
                    fa.save()
                    return redirect('tournament:free_agent')
        return redirect('tournament:free_agent')


def remove_entry(request, pk):
    free_agent = get_object_or_404(FreeAgent, pk=pk)
    if request.method == 'POST':
        if request.user == free_agent.player:
            free_agent.is_active = False
            free_agent.deleted = timezone.now()
            free_agent.save()
            return redirect('tournament:free_agent')
        else:
            return HttpResponse('Ошибка доступа')
    else:
        redirect('tournament:free_agent')


def update_entry(request, pk):
    free_agent = get_object_or_404(FreeAgent, pk=pk)
    if request.method == 'POST':
        if request.user == free_agent.player:
            free_agent.created = timezone.now()
            free_agent.save()
            return redirect('tournament:free_agent')
        else:
            return HttpResponse('Ошибка доступа')
    else:
        redirect('tournament:free_agent')


class TeamDetail(DetailView):
    model = Team
    context_object_name = 'team'
    template_name = 'tournament/teams/team_page.html'


class TeamList(ListView):
    queryset = Team.objects.all().order_by('-title')
    context_object_name = 'teams'
    template_name = 'tournament/teams/teams_list.html'


class LeagueDetail(DetailView):
    context_object_name = 'league'
    queryset = League.objects.filter(is_cup=False, priority=1, championship__is_active=True)
    template_name = 'tournament/premier_league/team_table.html'

    """
    a = Team.objects.values('title').filter(leagues=league).annotate(
        points=(
                Count(F('guest_matches'), distinct=True,
                      filter=Q(guest_matches__league=league, guest_matches__is_played=True), ) +
                Count(F('home_matches'), distinct=True,
                      filter=Q(home_matches__league=league, home_matches__is_played=True))
        )
    ).order_by('-points')
    print(a.query)
    for i in a:
        print(i)
"""

    #    works_query = Team.objects.filter(leagues=league).annotate(
    #        played_matchs=(Count('home_matches', filter=F('home_matches__is_played')) + Count('guest_matches', filter=F(
    #            'guest_matches__is_played')))).order_by('-played_matchs')
    #   Попробуем по-тупому, раз через запросик к Джанго-Орм кишка тонка(((((((
    """def get_queryset(self):
        try:
            league = League.objects.get(is_cup=False, championship__is_active=True, priority=1)
        except:
            league = None

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
"""


class MatchDetail(DetailView):
    model = Match
    context_object_name = 'match'
    template_name = 'tournament/match/detail.html'
