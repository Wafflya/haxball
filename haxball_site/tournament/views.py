from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count, F, Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import ListView, DetailView

from .forms import FreeAgentForm, EditTeamProfileForm
from .models import FreeAgent, Team, Match, League, Player
from core.forms import NewCommentForm
from core.models import NewComment, Profile


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


def edit_team_profile(request, slug):
    team = get_object_or_404(Team, slug=slug)
    if request.method == "POST" and (request.user == team.owner or request.user.is_superuser):
        form = EditTeamProfileForm(request.POST, instance=team)
        if form.is_valid():
            team = form.save(commit=False)
            team.save()
            return redirect(team.get_absolute_url())
    else:
        if request.user == team.owner or request.user.is_superuser:
            form = EditTeamProfileForm(instance=team)
        else:
            return HttpResponse('Ошибка доступа')
    return render(request, 'tournament/teams/edit_team.html', {'form': form})


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
    model = League
    # queryset = League.objects.filter(is_cup=False, championship__is_active=True)
    template_name = 'tournament/premier_league/team_table.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        league = context['league']

        comments_obj = NewComment.objects.filter(content_type=ContentType.objects.get_for_model(League),
                                                 object_id=league.id,
                                                 parent=None)
        print(comments_obj)
        paginate = Paginator(comments_obj, 25)
        page = self.request.GET.get('page')

        try:
            comments = paginate.page(page)
        except PageNotAnInteger:
            # If page is not an integer deliver the first page
            comments = paginate.page(1)
        except EmptyPage:
            # If page is out of range deliver last page of results
            comments = paginate.page(paginate.num_pages)

        context['page'] = page
        context['comments'] = comments
        comment_form = NewCommentForm()
        context['comment_form'] = comment_form
        return context


class MatchDetail(DetailView):
    model = Match
    context_object_name = 'match'
    template_name = 'tournament/match/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        match = context['match']

        comments_obj = NewComment.objects.filter(content_type=ContentType.objects.get_for_model(Match),
                                                 object_id=match.id,
                                                 parent=None)
        print(comments_obj)
        paginate = Paginator(comments_obj, 25)
        page = self.request.GET.get('page')

        try:
            comments = paginate.page(page)
        except PageNotAnInteger:
            # If page is not an integer deliver the first page
            comments = paginate.page(1)
        except EmptyPage:
            # If page is out of range deliver last page of results
            comments = paginate.page(paginate.num_pages)

        context['page'] = page
        context['comments'] = comments
        comment_form = NewCommentForm()
        context['comment_form'] = comment_form
        return context


def halloffame(request):
    top_goalscorers = Player.objects.annotate(
        goals_c=Count('goals__match__league')).filter(goals_c__gt=0).order_by('-goals_c')

    top_assistent = Player.objects.annotate(
        ass_c=Count('assists__match__league')).filter(ass_c__gt=0).order_by('-ass_c')
    top_clean_sheets = Player.objects.filter(event__event='CLN').annotate(
        event_c=Count('event__match__league')).filter(event_c__gt=0).order_by('-event_c')
    return render(request, 'tournament/hall_of_fame.html', {'goalscorers': top_goalscorers,
                                                            'assistents': top_assistent,
                                                            'clean_sheeters': top_clean_sheets,
                                                            })
