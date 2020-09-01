from django.urls import path

from .views import FreeAgentList, remove_entry, update_entry, TeamDetail, TeamList, LeagueDetail, MatchDetail, edit_team_profile

app_name = 'tournament'

urlpatterns = [
    path('free_agents/', FreeAgentList.as_view(), name='free_agent'),
    path('free_agents/remove/<int:pk>', remove_entry, name='remove_entry'),
    path('free_agents/update/<int:pk>', update_entry, name='update_entry'),
    path('team/<slug:slug>', TeamDetail.as_view(), name='team_detail'),
    path('team/<slug:slug>/edit', edit_team_profile, name='edit_team'),
    path('teams/', TeamList.as_view(), name='team_list'),
    path('<slug:slug>', LeagueDetail.as_view(), name='league'),
    path('match/<int:pk>', MatchDetail.as_view(), name='match_detail'),
]
