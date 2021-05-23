from django.core.management.base import BaseCommand

from ...models import League, TourNumber, Match
from ...templatetags.tournament_extras import sort_teams


class Command(BaseCommand):
    help = 'Generate shedule'

    def handle(self, *args, **options):
        league = League.objects.get(priority=1, championship__is_active=True, is_cup=False)
        teams = sort_teams(league)
        half = 8
        first_half = teams[:half]
        print(first_half)
        second_half = []
        for t in teams[half:]:
            if t.title != 'Дети Солнца':
                second_half.append(t)
        print(second_half)
        first_half_matches = []
        second_half_matches = []
        for i in Match.objects.filter(league=league):
            if (i.team_home in first_half) and (i.team_guest in first_half):
                first_half_matches.append(i)
            elif (i.team_home in second_half) and (i.team_guest in second_half):
                second_half_matches.append(i)

        print(first_half_matches)
        print('')
        print(second_half_matches)
