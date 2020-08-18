from django.http import HttpResponse
from django.shortcuts import render



def free_agent(request):
    return render(request, 'tournament/free_agent/free_agents_list.html')
