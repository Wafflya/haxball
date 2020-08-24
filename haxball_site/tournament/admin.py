from django.contrib import admin

# Register your models here.
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


class GoalInline(admin.StackedInline):
    model = Goal
    extra = 0


class EventInline(admin.StackedInline):
    model = OtherEvents
    extra = 0


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('league', 'tour_num', 'team_home', 'team_guest', 'is_played')
    fields = ['is_played', 'league', 'tour_num', 'match_date', ('team_home', 'team_guest'), ('team_home_start', 'team_guest_start')]
    inlines = [GoalInline, EventInline]


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('match', 'author', 'assistent',)