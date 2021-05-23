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

        # print(len(first_half_matches))
        # print(len(second_half_matches))
        pairs = half / 2

        """
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
        """
        print(len(first_half_matches))
        tours = [[] for i in range(0, half - 1)]
        for t in first_half:
            print(t)
            played_first = set()
            k = 0
            for jj in tours[k]:
                played_first.add(jj.team_home)
                played_first.add(jj.team_guest)
            print(played_first)
            to_del = []
            for m in first_half_matches:
                print(m)
                if (t == m.team_home or t == m.team_guest) and ((m.team_home not in played_first) and (m.team_guest not in played_first)):
                    tours[k].append(m)
                    to_del.append(m)
                    k += 1
                    if len(tours) > k:
                        played_first = set()
                        for jj in tours[k]:
                            played_first.add(jj.team_home)
                            played_first.add(jj.team_guest)
                    print(played_first)
                print('')
            for i in to_del:
                first_half_matches.pop(first_half_matches.index(i))
            print('')
            print(k)
        print(tours)
        print('')
