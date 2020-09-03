import datetime
import random
import time

from django.core.management.base import BaseCommand

from ...models import League, TourNumber, Match


class Command(BaseCommand):
    help = 'The Zen of Python'

    def handle(self, *args, **options):
        league = League.objects.get(priority=1, championship__is_active=True)
        teams = list(league.teams.all())
        half = len(teams) // 2
        n = len(teams)
        date_start = datetime.date(2020, 9, 7)
        cr_date = date_start
        time_delta = datetime.timedelta(days=2)

        date_cr_2 = datetime.date(2020, 10, 26)

        print('         Команды участницы:')
        for team in teams:
            print('     {}'.format(team.title))
        print()
        print('     Перемешиваем')
        random.shuffle(teams)
        for team in teams:
            print('     {}'.format(team.title))

        for i in range(1, len(teams)):
            tour = TourNumber.objects.create(number=i, league=league, date_from=cr_date, date_to=cr_date + time_delta)
            cr_date = cr_date + time_delta + datetime.timedelta(days=1)
            tour_reverse = TourNumber.objects.create(number=i + n - 1, league=league, date_from=date_cr_2,
                                                     date_to=date_cr_2 + time_delta)
            date_cr_2 = date_cr_2 + time_delta + datetime.timedelta(days=1)
            print('                 Тур {}'.format(tour))
            for j in range(half):
                match = Match.objects.create(team_home=teams[j], team_guest=teams[n - 1 - j], numb_tour=tour,
                                             league=league)
                match_reverse = Match.objects.create(team_guest=teams[j], team_home=teams[n - 1 - j],
                                                     numb_tour=tour_reverse,
                                                     league=league)
                print('          {}  -  {}'.format(match.team_home.title, match.team_guest.title))
            teams.insert(1, teams.pop())

        print()
        print('     Генерация расписания завершена')
        print("           Удачного чемпионата!")
