from django.shortcuts import get_object_or_404, redirect

from .models import Question, Choice


def poll_add_vote(request, pk):
    #print(request.POST)
    choice = get_object_or_404(Choice, pk=int(request.POST[str(pk)]))
    if request.method == 'POST':
        choice.votes.add(request.user)
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect(request.META.get('HTTP_REFERER'))
