from django.urls import path
from .views import FreeAgentList, remove_entry, update_entry

app_name = 'tournament'

urlpatterns = [
    path('free_agents/', FreeAgentList.as_view(), name='free_agent'),
    path('free_agents/remove/<int:pk>', remove_entry, name='remove_entry'),
    path('free_agents/update/<int:pk>', update_entry, name='update_entry'),
]