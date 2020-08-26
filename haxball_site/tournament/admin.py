# Register your models here.
from django.contrib import admin

from .models import FreeAgent, Player, League, Team, Match, Goal, OtherEvents, Substitution, Season


@admin.register(FreeAgent)
class FreeAgentAdmin(admin.ModelAdmin):
    list_display = ('id', 'player', 'position_main', 'description', 'is_active', 'created', 'deleted')


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'nickname','team', 'nation', 'role',)
    raw_id_fields = ('name',)





@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('title', 'short_title', 'owner',)


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created')


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ('title', 'priority', 'created')
    filter_horizontal = ('teams',)


"""
class GoalAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(GoalAdminForm, self).__init__(*args, **kwargs)
        print(kwargs)
        if self.instance.match:
            self.fields['team'].queryset = Team.objects.filter(
            Q(home_matches=self.instance.match) | Q(guest_matches=self.instance.match))

           # Team.objects.filter(
           # Q(home_matches=self.instance.match) | Q(guest_matches=self.instance.match))
"""


class GoalInline(admin.StackedInline):
    model = Goal
    extra = 3


class SubstitutionInline(admin.StackedInline):
    model = Substitution
    extra = 3


class EventInline(admin.StackedInline):
    model = OtherEvents
    extra = 2


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('league', 'tour_num', 'team_home', 'team_guest', 'is_played', 'updated')
    fieldsets = (
        ('Основная инфа', {
            'fields': (('league', 'tour_num', 'is_played', 'match_date'),)
        }),
        (None, {
            'fields': (('team_home', 'team_guest', 'replay_link', 'inspector'),)
        }),
        ('Составы', {
            'classes': ('grp-collapse grp-closed',),
            'fields': ('team_home_start', 'team_guest_start',)
        })
    )
    # fields = ['is_played', 'league', 'tour_num', 'match_date', ('team_home', 'team_guest'),
    #          ('team_home_start', 'team_guest_start')]
    inlines = [GoalInline, SubstitutionInline, EventInline]


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('match', 'author', 'assistent')


@admin.register(Substitution)
class SubstitutionAdmin(admin.ModelAdmin):
    list_display = ('match', 'player_out', 'player_in')


@admin.register(OtherEvents)
class OtherEventsAdmin(admin.ModelAdmin):
    list_display = ('match', 'author',)


"""
@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    form = GoalAdminForm
    list_display = ('match', 'author', 'assistent',)
"""
