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

class EventInline(admin.StackedInline):
    model = OtherEvents


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('league', 'tour_num', 'team_home', 'team_guest')
    inlines = [GoalInline, EventInline]
