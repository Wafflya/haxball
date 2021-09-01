from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from ...models import League, TourNumber, Match, Season, Player


class Command(BaseCommand):
    help = 'Всех в СА'

    def add_arguments(self, parser):
        parser.add_argument('champ_number', default=0, nargs='?', type=int, )

    def handle(self, *args, **options):
        print(options['champ_number'])
        try:
            seas = Season.objects.get(number=options['champ_number'])
        except:
            print('Видимо похер')
            raise CommandError('Выбран несуществующий сезон')

        players_in_team = Player.objects.filter(~Q(team=None))

        print('Выборка по сезону {}'.format(options['champ_number']))
        for p in players_in_team:
            print(p)

