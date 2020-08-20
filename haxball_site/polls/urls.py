from django.urls import path

from .views import poll_add_vote

app_name = 'polls'

urlpatterns = [
    path('poll_vote/<int:pk>/add', poll_add_vote, name='add_user_vote'),
]
