# Register your models here.
from django.contrib import admin
from django.db.models import Q
from django.urls import resolve

from .models import FreeAgent, Player, League, Team, Match, Goal, OtherEvents, Substitution, Season, PlayerTransfer, \
    TourNumber, Nation, Achievements
from django import forms


@admin.register(FreeAgent)
class FreeAgentAdmin(admin.ModelAdmin):
    list_display = ('id', 'player', 'position_main', 'description', 'is_active', 'created', 'deleted')


@admin.register(Achievements)
class AchievmentsAdmin(admin.ModelAdmin):
    list_display = ('id', 'position_number', 'title', 'description', 'image', 'mini_image')
    filter_horizontal = ('player',)


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'nickname', 'team', 'player_nation', 'role',)
    raw_id_fields = ('name',)
    list_filter = ('role','team','name')
    search_fields = ('nickname','name__username',)

@admin.register(PlayerTransfer)
class PlayerTransferAdmin(admin.ModelAdmin):
    list_display = ('trans_player', 'to_team', 'date_join', 'season_join')
    list_filter = ('trans_player', 'to_team',)


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


@admin.register(Nation)
class NationAdmin(admin.ModelAdmin):
    list_display = ('country',)


class GoalInline(admin.StackedInline):
    model = Goal
    extra = 3

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        resolved = resolve(request.path_info)
        not_found = False
        try:
            match = self.parent_model.objects.get(id=resolved.kwargs['object_id'])
        except:
            not_found = True
        if db_field.name == "team" and not not_found:
            kwargs["queryset"] = Team.objects.filter(Q(home_matches=match) | Q(guest_matches=match)).distinct()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class SubstitutionInline(admin.StackedInline):
    model = Substitution
    extra = 3

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        resolved = resolve(request.path_info)
        not_found = False
        try:
            match = self.parent_model.objects.get(id=resolved.kwargs['object_id'])
        except:
            not_found = True
        if db_field.name == "team" and not not_found:
            kwargs["queryset"] = Team.objects.filter(Q(home_matches=match) | Q(guest_matches=match)).distinct()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class EventInline(admin.StackedInline):
    model = OtherEvents
    extra = 2

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        resolved = resolve(request.path_info)
        not_found = False
        try:
            match = self.parent_model.objects.get(id=resolved.kwargs['object_id'])
        except:
            not_found = True
        if db_field.name == "team" and not not_found:
            kwargs["queryset"] = Team.objects.filter(Q(home_matches=match) | Q(guest_matches=match)).distinct()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = (
        'league', 'numb_tour', 'team_home', 'score_home', 'team_guest', 'score_guest', 'is_played', 'updated',
        'inspector', 'id',)
    # readonly_fields = ('score_home', 'score_guest',)
    filter_horizontal = ('team_home_start', 'team_guest_start',)
    list_filter = ('numb_tour__number', 'league', 'inspector', 'is_played')
    fieldsets = (
        ('Основная инфа', {
            'fields': (('league', 'is_played', 'match_date', 'numb_tour',),)
        }),
        (None, {
            'fields': (('team_home', 'team_guest', 'replay_link',),)
        }),
        (None, {
            'fields': (('score_home', 'score_guest', 'inspector', 'replay_link_second'),)
        }),
        ('Составы', {
            'classes': ('grp-collapse grp-closed',),
            'fields': ('team_home_start', 'team_guest_start',)
        }),
        ('Комментарий:', {
            'classes': ('grp-collapse grp-closed',),
            'fields': ('comment',)
        })
    )
    # fields = ['is_played', 'league', 'tour_num', 'match_date', ('team_home', 'team_guest'),
    #          ('team_home_start', 'team_guest_start')]
    inlines = [GoalInline, SubstitutionInline, EventInline]


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('match', 'author', 'assistent', 'id')


@admin.register(Substitution)
class SubstitutionAdmin(admin.ModelAdmin):
    list_display = ('match', 'player_out', 'player_in')


@admin.register(OtherEvents)
class OtherEventsAdmin(admin.ModelAdmin):
    list_display = ('event', 'match', 'author',)


@admin.register(TourNumber)
class MatchTourAdmin(admin.ModelAdmin):
    list_display = ('number', 'league', 'is_actual', 'date_from', 'date_to')
    list_editable = ('is_actual',)
    list_filter = ('league','number')


"""
@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    form = GoalAdminForm
    list_display = ('match', 'author', 'assistent',)
"""
