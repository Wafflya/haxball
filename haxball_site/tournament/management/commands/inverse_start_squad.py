from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.utils import timezone

from ...models import League, TourNumber, Match, Season, Player, PlayerTransfer


class Command(BaseCommand):
    help = 'Перепутали составы стартовые'

    def add_arguments(self, parser):
        parser.add_argument('match_number', default=0, nargs='?', type=int, )

    def handle(self, *args, **options):
        print(options['match_number'])
        try:
            match = Match.objects.get(id=options['match_number'])
        except:
            print('Видимо похер')
            raise CommandError('Выбран несуществующий сезон')

        s = []

        print(match.team_home_start.all())
        print(match.team_guest_start.all())

        for i in match.team_home_start.all():
            s.append(i)
        match.team_home_start.clear()
        for i in match.team_guest_start.all():
            match.team_home_start.add(i)
        match.team_guest_start.clear()
        for i in s:
            match.team_guest_start.add(i)

        print(match.team_home_start.all())
        print(match.team_guest_start.all())
