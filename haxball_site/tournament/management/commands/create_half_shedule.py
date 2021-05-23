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

        print(len(first_half_matches))
        print(len(second_half_matches))
        pairs = half/2
        tours = []
        k = 0
        for i in range(1,half):
            played_first = set()
            played_second = set()
            t_i = []
            for m in first_half_matches:
                if (m.team_home not in played_first) and (m.team_guest not in played_first):
                    played_first.add(m.team_home)
                    played_first.add(m.team_guest)
                    t_i.append(m)
                    k += 1
                if len(played_first) == half:
                    break

            for jj in t_i:
                first_half_matches.pop(first_half_matches.index(jj))

            print(t_i)
            print(len(first_half_matches))
            tours.append(t_i)
            
        print(k)
        print(first_half_matches)
        print(tours)


        print(first_half_matches)
        print('')
        print(second_half_matches)
