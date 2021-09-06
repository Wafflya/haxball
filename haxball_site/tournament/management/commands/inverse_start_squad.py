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

        print(match.team_home_start.all())