from django import template
from django.db.models import Count, Max

from ..models import Question, Choice

register = template.Library()


@register.inclusion_tag('polls/include/polls_list.html')
def polls_list(count, user):
    active_polls = Question.objects.filter(is_active=True)
    return {'active_polls': active_polls,
            'user': user}


@register.filter
def user_in_poll(user, poll):
    a = poll.choices.all().filter(votes=user)
    if a:
        return True
    else:
        return False

@register.filter
def percent_choices(choice, poll):
    all = Question.objects.filter(id=poll.id).aggregate(all_votes = Count('choices__votes'))
    return round(100*choice.votes.count()/all['all_votes'])

@register.filter
def most_popular_choice(choice, poll):
    most = Choice.objects.filter(question=poll).annotate(count = Count('votes')).aggregate(most_pop = Max('count'))
    return choice.votes.count() == most['most_pop']