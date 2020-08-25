# Register your models here.
from django import forms
from django.contrib import admin
from django.db.models import Q

from .models import FreeAgent, Player, League, Team, Match, Goal, OtherEvents


@admin.register(FreeAgent)
class FreeAgentAdmin(admin.ModelAdmin):
    list_display = ('id', 'player', 'position_main', 'description', 'is_active', 'created', 'deleted')


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'team', 'nation', 'role',)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('title', 'short_title', 'owner', 'league')


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active',)

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


class EventInline(admin.StackedInline):
    model = OtherEvents
    extra = 2


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('league', 'tour_num', 'team_home', 'team_guest', 'is_played')
    fields = ['is_played', 'league', 'tour_num', 'match_date', ('team_home', 'team_guest'), ('team_home_start', 'team_guest_start')]
    inlines = [GoalInline, EventInline]

"""
@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    form = GoalAdminForm
    list_display = ('match', 'author', 'assistent',)
"""