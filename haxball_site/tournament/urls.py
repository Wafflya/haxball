from django.urls import path
from . import views

app_name = 'tournament'

urlpatterns = [
    path('free_agents/', views.free_agent, name='free_agent'),
]