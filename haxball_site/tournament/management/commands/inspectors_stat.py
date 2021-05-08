import datetime
import random
import time

from django.core.management.base import BaseCommand, CommandError

from ...models import League, TourNumber, Match, Season


class Command(BaseCommand):
    help = 'Считаем активность инспекторов'

    def add_arguments(self, parser):
        parser.add_argument('champ_number', default=0, nargs='?', type=int, )

    def handle(self, *args, **options):
        print(options['champ_number'])
        if options['champ_number'] == 0:
            print('Выборка по всем сезонам')
            all_matches = Match.objects.filter(is_played=True)
        else:
            try:
                ses = Season.objects.get(number=options['champ_number'])
            except:
                raise CommandError('Выбран несуществующий сезон')

            print('Выборка по сезону {}'.format(options['champ_number']))
            all_matches = Match.objects.filter(league__championship=ses, is_played=True)
        inspectors = {}
        for m in all_matches:
            print(m.inspector)
            if m.inspector in inspectors.keys():
                inspectors[m.inspector].append(m)
            else:
                inspectors[m.inspector] = []

        print("Инспектор  М  Г  другое")
        for inspector in inspectors:
            goals_added = 0
            other_event_added = 0
            for m in inspectors[inspector]:
                goals_added += m.match_goal.count()
                other_event_added += m.match_substitutions.count()+m.match_event.count()
            print(inspector,len(inspectors[inspector]),goals_added, other_event_added, goals_added+other_event_added)